import Card from './Card'

function SectionContainer({ title, children, className = '' }) {
  return (
    <Card as="section" className={`p-6 ${className}`.trim()}>
      <h2 className="mb-4 text-lg font-semibold text-[#24292f]">{title}</h2>
      <div className="text-sm text-[#57606a]">{children}</div>
    </Card>
  )
}

export default SectionContainer
