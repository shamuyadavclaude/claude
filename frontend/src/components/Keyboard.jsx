const ALPHABET = 'abcdefghijklmnopqrstuvwxyz'.split('')

export default function Keyboard({ guessed, word, onGuess }) {
  return (
    <div className="keyboard">
      {ALPHABET.map((letter) => {
        const isGuessed = guessed.includes(letter)
        const isCorrect = isGuessed && word.includes(letter)
        const isWrong   = isGuessed && !word.includes(letter)
        return (
          <button
            key={letter}
            className={`key ${isCorrect ? 'correct' : ''} ${isWrong ? 'wrong' : ''}`}
            disabled={isGuessed}
            onClick={() => onGuess(letter)}
          >
            {letter.toUpperCase()}
          </button>
        )
      })}
    </div>
  )
}
