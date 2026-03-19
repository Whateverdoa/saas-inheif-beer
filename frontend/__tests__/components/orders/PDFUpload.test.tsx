import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { PDFUpload } from '@/components/orders/PDFUpload'

describe('PDFUpload', () => {
  const mockOnFileSelect = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should render dropzone with correct text', () => {
    render(<PDFUpload onFileSelect={mockOnFileSelect} />)
    
    expect(screen.getByText(/drag.*drop.*pdf/i)).toBeInTheDocument()
  })

  it('should display file when selected', async () => {
    const user = userEvent.setup()
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' })
    
    render(<PDFUpload onFileSelect={mockOnFileSelect} />)
    
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement
    await user.upload(fileInput, file)
    
    await waitFor(() => {
      expect(screen.getByText(/test\.pdf/i)).toBeInTheDocument()
    })
  })

  it('should call onFileSelect when file is selected', async () => {
    const user = userEvent.setup()
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' })
    
    render(<PDFUpload onFileSelect={mockOnFileSelect} />)
    
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement
    await user.upload(fileInput, file)
    
    await waitFor(() => {
      expect(mockOnFileSelect).toHaveBeenCalledWith(file)
    })
  })

  it('should show upload progress when uploading', () => {
    render(<PDFUpload onFileSelect={mockOnFileSelect} isUploading={true} uploadProgress={50} />)
    
    expect(screen.getByRole('progressbar')).toBeInTheDocument()
    expect(screen.getByText(/50%/i)).toBeInTheDocument()
  })

  it('should disable input when uploading', () => {
    render(<PDFUpload onFileSelect={mockOnFileSelect} isUploading={true} />)
    
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement
    expect(fileInput.disabled).toBe(true)
  })
})

