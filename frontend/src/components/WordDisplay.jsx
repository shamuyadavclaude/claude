export default function WordDisplay({ display }) {
  return (
    <div className="word-display">
      {display.map((item, i) => (
        <div key={i} className="letter-box">
          <span className={`letter-char ${item.revealed ? 'revealed' : ''}`}>
            {item.revealed ? item.char.toUpperCase() : '\u00A0'}
          </span>
          <div className="letter-underline" />
        </div>
      ))}
    </div>
  )
}
