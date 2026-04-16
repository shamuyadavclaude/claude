import { useState, useEffect } from 'react'
import Gallows from './components/Gallows'
import WordDisplay from './components/WordDisplay'
import Keyboard from './components/Keyboard'
import './App.css'

const INIT = { game_id: null, display: [], guessed: [], wrong_letters: [], wrong_count: 0, status: 'loading', category: '', hint: '', max_wrong: 6, word: '' }

export default function App() {
  const [game, setGame] = useState(INIT)

  const startNew = async () => {
    setGame(INIT)
    const res  = await fetch('/api/new', { method: 'POST' })
    const data = await res.json()
    setGame({ ...data, word: data.display.map(d => d.char).join('') })
  }

  const handleGuess = async (letter) => {
    if (game.status !== 'playing') return
    const res  = await fetch('/api/guess', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({
        game_id:     game.game_id,
        letter,
        word:        game.word,
        guessed:     game.guessed,
        wrong_count: game.wrong_count,
        status:      game.status,
      }),
    })
    const data = await res.json()
    setGame(prev => ({ ...prev, ...data }))
  }

  useEffect(() => { startNew() }, [])

  if (game.status === 'loading') {
    return <div className="loading">Loading…</div>
  }

  return (
    <div className="container">
      <h1>Hangman</h1>
      <div className="game-area">
        <div className="left-panel">
          <Gallows wrongCount={game.wrong_count} />
          <div className="status-bar">
            <span>Wrong: <b>{game.wrong_count}</b> / {game.max_wrong}</span>
            <span>Category: <b>{game.category}</b></span>
          </div>
        </div>

        <div className="right-panel">
          <div className="hint-box">Hint: {game.hint}</div>

          <WordDisplay display={game.display} />

          <div className="wrong-letters">
            <span className="label">Missed: </span>
            {game.wrong_letters.map(ch => (
              <span key={ch} className="wrong-letter">{ch.toUpperCase()}</span>
            ))}
          </div>

          {game.status === 'won' && (
            <div className="message win">
              <p className="msg-title">You Won! 🎉</p>
              <p className="reveal">The word was <b>{game.word?.toUpperCase()}</b></p>
              <button className="btn-new" onClick={startNew}>Play Again</button>
            </div>
          )}

          {game.status === 'lost' && (
            <div className="message lose">
              <p className="msg-title">Game Over!</p>
              <p className="reveal">The word was <b>{game.word?.toUpperCase()}</b></p>
              <button className="btn-new" onClick={startNew}>Play Again</button>
            </div>
          )}

          {game.status === 'playing' && (
            <Keyboard guessed={game.guessed} word={game.word} onGuess={handleGuess} />
          )}

          <div style={{ textAlign: 'center', marginTop: '12px' }}>
            <button className="btn-restart" onClick={startNew}>New Word</button>
          </div>
        </div>
      </div>
    </div>
  )
}
