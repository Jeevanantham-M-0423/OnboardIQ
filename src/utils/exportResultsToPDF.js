import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'

export async function exportResultsToPDF(elementId, filename = 'results.pdf') {
  const input = document.getElementById(elementId)
  if (!input) return

  // Use html2canvas to render the element to a canvas
  const canvas = await html2canvas(input, { scale: 2, backgroundColor: '#0d1117' })
  const imgData = canvas.toDataURL('image/png')
  const pdf = new jsPDF({ orientation: 'portrait', unit: 'pt', format: 'a4' })

  // Calculate width/height to fit A4
  const pageWidth = pdf.internal.pageSize.getWidth()
  const pageHeight = pdf.internal.pageSize.getHeight()
  const imgWidth = pageWidth
  const imgHeight = (canvas.height * pageWidth) / canvas.width

  let position = 0
  pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)

  // If content is longer than one page, add more pages
  if (imgHeight > pageHeight) {
    let remainingHeight = imgHeight - pageHeight
    while (remainingHeight > 0) {
      position = position - pageHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      remainingHeight -= pageHeight
    }
  }

  pdf.save(filename)
}
