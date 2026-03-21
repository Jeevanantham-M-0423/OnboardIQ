const BASE_CLASSES =
  'inline-flex cursor-pointer items-center justify-center rounded-lg px-4 py-2 text-sm font-medium transition-all duration-200 hover:shadow-md active:scale-95 disabled:cursor-not-allowed disabled:opacity-60 disabled:active:scale-100 disabled:hover:shadow-none'

const VARIANT_CLASSES = {
  primary: 'bg-[#238636] text-white hover:bg-[#2ea043]',
  secondary: 'border border-[#30363d] bg-[#161b22] text-[#c9d1d9] hover:bg-[#21262c]',
}

function Button({ children, type = 'button', variant = 'primary', className = '', ...props }) {
  const selectedVariant = VARIANT_CLASSES[variant] || VARIANT_CLASSES.primary

  return (
    <button type={type} className={`${BASE_CLASSES} ${selectedVariant} ${className}`.trim()} {...props}>
      {children}
    </button>
  )
}

export default Button
