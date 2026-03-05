import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

function Home() {
  const [query, setQuery] = useState('')
  const navigate = useNavigate()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!query.trim()) return

    // Generate a session ID and navigate to chat
    const sessionId = crypto.randomUUID()
    navigate(`/chat/${sessionId}`, { state: { initialQuery: query.trim() } })
    setQuery('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e as any)
    }
  }

  return (
    <div className="home">
      <div className="home-header">
        <img src="/studybuddy-logo.svg" alt="StudyBuddy AI" className="home-logo" />
        <h1>StudyBuddy AI</h1>
        <p>Tu tutor inteligente 24/7</p>
      </div>

      <div className="home-chat-container">
        <form onSubmit={handleSubmit} className="home-chat-form">
          <div className="home-input-container">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="¿Qué tema quieres aprender hoy?"
              className="home-chat-input"
              rows={3}
            />
            <button
              type="submit"
              disabled={!query.trim()}
              className="home-send-button"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="m22 2-7 20-4-9-9-4z"/>
                <path d="M22 2 11 13"/>
              </svg>
            </button>
          </div>
        </form>
      </div>

      <div className="home-examples">
        <p className="examples-label">Try asking:</p>
        <div className="example-queries">
          <button
            className="example-query"
            onClick={() => setQuery("Explícame el ciclo del agua paso a paso")}
          >
            "Explícame el ciclo del agua paso a paso"
          </button>
          <button
            className="example-query"
            onClick={() => setQuery("¿Cuáles son las leyes de Newton?")}
          >
            "¿Cuáles son las leyes de Newton?"
          </button>
          <button
            className="example-query"
            onClick={() => setQuery("Ayúdame a entender las fracciones con ejemplos")}
          >
            "Ayúdame a entender las fracciones con ejemplos"
          </button>
        </div>
      </div>
    </div>
  )
}

export default Home
