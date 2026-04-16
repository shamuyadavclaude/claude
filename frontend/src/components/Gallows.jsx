export default function Gallows({ wrongCount }) {
  const show = (n) => wrongCount >= n

  return (
    <svg viewBox="0 0 200 250" className="gallows" xmlns="http://www.w3.org/2000/svg">
      <line x1="20"  y1="230" x2="180" y2="230" stroke="#555" strokeWidth="4" strokeLinecap="round"/>
      <line x1="60"  y1="230" x2="60"  y2="20"  stroke="#555" strokeWidth="4" strokeLinecap="round"/>
      <line x1="60"  y1="20"  x2="130" y2="20"  stroke="#555" strokeWidth="4" strokeLinecap="round"/>
      <line x1="130" y1="20"  x2="130" y2="45"  stroke="#555" strokeWidth="4" strokeLinecap="round"/>
      {show(1) && <circle cx="130" cy="62" r="17" stroke="#e74c3c" strokeWidth="3" fill="none"/>}
      {show(2) && <line x1="130" y1="79"  x2="130" y2="148" stroke="#e74c3c" strokeWidth="3" strokeLinecap="round"/>}
      {show(3) && <line x1="130" y1="98"  x2="100" y2="128" stroke="#e74c3c" strokeWidth="3" strokeLinecap="round"/>}
      {show(4) && <line x1="130" y1="98"  x2="160" y2="128" stroke="#e74c3c" strokeWidth="3" strokeLinecap="round"/>}
      {show(5) && <line x1="130" y1="148" x2="100" y2="188" stroke="#e74c3c" strokeWidth="3" strokeLinecap="round"/>}
      {show(6) && <line x1="130" y1="148" x2="160" y2="188" stroke="#e74c3c" strokeWidth="3" strokeLinecap="round"/>}
    </svg>
  )
}
