
function Card({ children, className = '', as: Component = 'div' }) {
  return (
    <Component
      className={`rounded-xl border border-[#30363d] bg-[#161b22] shadow-md transition-all duration-200 hover:shadow-lg ${className}`.trim()}
    >
      {children}
    </Component>
  )
}

export default Card
