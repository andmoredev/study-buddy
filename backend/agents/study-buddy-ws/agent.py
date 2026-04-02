"""
Generic Assistant Agent - AgentCore Runtime with WebSocket Streaming

A conversational assistant with:
- Real-time streaming via WebSocket
- Memory persistence across conversations
- JWT-based user authentication
- Tool access (memory, LLM)

Required Environment Variables:
    - AGENTCORE_MEMORY_ID: AgentCore Memory resource ID for conversation persistence

Optional Environment Variables:
    - AWS_REGION: AWS region (default: us-east-1)
    - BEDROCK_MODEL_ID: Bedrock model ID (default: us.amazon.nova-lite-v1:0)
"""

import os
import json
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands_tools import current_time
from strands.models import BedrockModel
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

app = BedrockAgentCoreApp()

# ============================================================================
# Configuration
# ============================================================================

AGENTCORE_MEMORY_ID = os.environ.get("AGENTCORE_MEMORY_ID")
AWS_REGION = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "us.amazon.nova-lite-v1:0")

if not AGENTCORE_MEMORY_ID:
    raise ValueError("AGENTCORE_MEMORY_ID environment variable is required but not set")

# ============================================================================

SYSTEM_PROMPT = """Eres StudyBuddy AI, un tutor educativo inteligente diseñado para ayudar a estudiantes a aprender de forma clara, efectiva y motivadora. Tu misión es acompañar al estudiante en su proceso de aprendizaje con paciencia y entusiasmo.

## Principios de enseñanza

1. **Lenguaje simple y claro**: Explica los conceptos usando palabras sencillas y accesibles. Evita jerga técnica innecesaria y, cuando debas usarla, defínela de inmediato.

2. **Explicaciones paso a paso**: Desglosa cada tema en pasos ordenados o puntos clave. Usa listas numeradas o viñetas para que la información sea fácil de seguir.

3. **Ejemplos concretos**: Acompaña cada explicación con ejemplos prácticos y situaciones de la vida real que ayuden al estudiante a visualizar el concepto.

4. **De lo simple a lo complejo**: Comienza siempre con la explicación más básica y ve añadiendo detalle progresivamente. Para preguntas complejas, construye el conocimiento capa por capa.

5. **Fomentar la curiosidad**: Anima al estudiante a seguir explorando y aprendiendo. Haz preguntas que despierten su interés y conecta los temas con aplicaciones interesantes del mundo real.

6. **Práctica activa**: Cuando sea relevante, ofrece crear preguntas de práctica, cuestionarios cortos o resúmenes para reforzar lo aprendido. Pregunta al estudiante si desea practicar después de cada explicación.

7. **Tono amigable y paciente**: Mantén siempre un tono cercano, positivo, alentador y paciente. Celebra los avances del estudiante y nunca hagas que se sienta mal por no entender algo. Frases como "¡Excelente pregunta!" o "Es normal que esto sea confuso al principio" son bienvenidas.

## Formato de respuestas

- Usa formato Markdown para estructurar tus respuestas: encabezados (##), negritas (**texto**), listas y bloques de código cuando sea apropiado.
- Organiza la información con encabezados claros y secciones bien definidas.
- Usa emojis educativos con moderación (📚, 💡, ✅, 🔑) para hacer las respuestas más visuales y atractivas.

## Manejo de preguntas fuera de tema

Si el estudiante hace una pregunta que no está relacionada con temas educativos o de aprendizaje, redirige la conversación de forma amable hacia el aprendizaje. Por ejemplo: "¡Esa es una pregunta interesante! Sin embargo, mi especialidad es ayudarte a aprender. ¿Hay algún tema académico en el que pueda ayudarte hoy?"

## Memoria

Utiliza tu herramienta de memoria para recordar el contexto de conversaciones anteriores cuando sea relevante, y así ofrecer una experiencia de aprendizaje continua y personalizada."""


def create_session_manager(runtime_session_id: str, user_id: str = None):
    """Create AgentCore Memory session manager for conversation persistence."""
    actor_id = user_id if user_id else "user"

    config = AgentCoreMemoryConfig(
        memory_id=AGENTCORE_MEMORY_ID,
        session_id=runtime_session_id,
        actor_id=actor_id
    )

    return AgentCoreMemorySessionManager(
        agentcore_memory_config=config,
        region_name=AWS_REGION
    )


@app.websocket
async def websocket_handler(websocket, context):
    """
    WebSocket handler for real-time streaming agent responses.

    AWS SigV4 authentication is handled by AgentCore Runtime before this handler is called.
    User identity is passed via custom headers in the WebSocket connection.

    Args:
        websocket: WebSocket connection object
        context: Request context containing headers and request information
    """
    await websocket.accept()

    agent = None
    session_id = None

    try:
        # Extract user identity from custom headers
        # These are passed as query parameters with prefix X-Amzn-Bedrock-AgentCore-Runtime-Custom-
        # and received as lowercase headers in context.request_headers
        headers = context.request_headers or {}
        user_id = headers.get("x-amzn-bedrock-agentcore-runtime-custom-user-id")

        print(f"WebSocket connected - User: {user_id}, Context session: {context.session_id}")

        # Message loop — keep connection open for multi-turn conversation
        while True:
            data = await websocket.receive_json()
            request = data.get("request", "")
            msg_session_id = data.get("session_id")

            # Validate input
            if not request:
                await websocket.send_json({
                    "type": "error",
                    "error": "Missing required field: request"
                })
                continue

            if not msg_session_id:
                await websocket.send_json({
                    "type": "error",
                    "error": "Missing required field: session_id"
                })
                continue

            print(f"Request received - Session: {msg_session_id}")

            # Create agent on first message, or recreate if session changes
            if agent is None or msg_session_id != session_id:
                session_id = msg_session_id
                session_manager = create_session_manager(session_id, user_id)

                agent = Agent(
                    agent_id="assistant",
                    model=BedrockModel(model_id=BEDROCK_MODEL_ID),
                    tools=[current_time],
                    system_prompt=SYSTEM_PROMPT,
                    session_manager=session_manager,
                )
                print(f"Agent initialized - Model: {BEDROCK_MODEL_ID}, Session: {session_id}, Messages loaded: {len(agent.messages)}")

            print(f"Messages in context: {len(agent.messages)}")

            # Stream events back to client in real-time
            # Track thinking tag state across chunks
            in_thinking = False
            thinking_buffer = ""

            async for event in agent.stream_async(request):
                # Extract only JSON-serializable data from the event.
                # stream_async() can yield events containing non-serializable objects
                # (e.g. the Agent instance in completion events), so we pick out
                # the fields the client actually needs.

                if event.get("data"):
                    chunk = event["data"]

                    # Parse <thinking>...</thinking> tags out of the data stream.
                    # The model emits these as plain text deltas mixed with normal output.
                    while chunk:
                        if in_thinking:
                            if "</thinking>" in chunk:
                                end_idx = chunk.index("</thinking>")
                                thinking_buffer += chunk[:end_idx]
                                chunk = chunk[end_idx + len("</thinking>"):]
                                in_thinking = False
                                if thinking_buffer.strip():
                                    await websocket.send_json({
                                        "type": "stream_event",
                                        "event": {"thinking": thinking_buffer.strip()}
                                    })
                                thinking_buffer = ""
                            else:
                                thinking_buffer += chunk
                                chunk = ""
                        else:
                            if "<thinking>" in chunk:
                                start_idx = chunk.index("<thinking>")
                                before = chunk[:start_idx]
                                chunk = chunk[start_idx + len("<thinking>"):]
                                in_thinking = True
                                if before:
                                    await websocket.send_json({
                                        "type": "stream_event",
                                        "event": {"data": before}
                                    })
                            else:
                                await websocket.send_json({
                                    "type": "stream_event",
                                    "event": {"data": chunk}
                                })
                                chunk = ""

                elif event.get("current_tool_use"):
                    tool = event["current_tool_use"]
                    tool_name = tool.get("name")
                    if tool_name:
                        print(f"Tool use: {tool_name}")
                        await websocket.send_json({
                            "type": "stream_event",
                            "event": {"current_tool_use": {"name": tool_name, "tool_use_id": tool.get("tool_use_id")}}
                        })

                elif event.get("init_event_loop"):
                    await websocket.send_json({
                        "type": "stream_event",
                        "event": {"init_event_loop": True}
                    })

                elif event.get("complete"):
                    await websocket.send_json({
                        "type": "stream_event",
                        "event": {"complete": True}
                    })

            # Send completion signal for this turn
            await websocket.send_json({
                "type": "complete",
                "session_id": session_id
            })

            print(f"Response complete - Session: {session_id}, Messages: {len(agent.messages)}")

    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "error": "Invalid JSON in request"
            })
        except:
            pass  # Connection may already be closed

    except Exception as e:
        error_str = str(e)
        # WebSocket disconnect is expected when client closes the connection
        if "disconnect" in error_str.lower() or "closed" in error_str.lower():
            print(f"🔌 Client disconnected (session: {session_id})")
        else:
            print(f"❌ Error in websocket_handler: {error_str}")
            import traceback
            traceback.print_exc()

            try:
                await websocket.send_json({
                    "type": "error",
                    "error": error_str,
                    "message": "An error occurred while processing your request"
                })
            except:
                pass  # Connection may already be closed

    finally:
        try:
            await websocket.close()
            print(f"🔌 WebSocket connection closed (session: {session_id})")
        except:
            pass


@app.entrypoint
def invoke(payload):
    """HTTP entrypoint for synchronous invocation."""
    request = payload.get("request", "")

    if not request:
        return {"error": "Please provide a request"}

    try:
        runtime_session_id = payload.get("session_id")
        user_id = payload.get("user_id")

        if not runtime_session_id:
            import uuid
            runtime_session_id = f"session_{uuid.uuid4().hex[:16]}"
            print(f"Warning: Generated session ID: {runtime_session_id}")

        session_manager = create_session_manager(runtime_session_id, user_id)

        agent = Agent(
            agent_id="assistant",
            model=BedrockModel(model_id=BEDROCK_MODEL_ID),
            tools=[current_time],
            system_prompt=SYSTEM_PROMPT,
            session_manager=session_manager,
        )

        print(f"Agent initialized with model: {BEDROCK_MODEL_ID}, session: {runtime_session_id}")
        print(f"Messages loaded from memory: {len(agent.messages)}")

        result = agent(request)

        return {
            "request": request,
            "response": str(result),
        }

    except Exception as e:
        return {
            "error": "INTERNAL_SERVER_ERROR",
            "message": f"An error occurred while processing your request: {str(e)}",
        }


if __name__ == "__main__":
    app.run()
