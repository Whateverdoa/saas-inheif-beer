import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { OrderForm } from '@/components/orders/OrderForm'

jest.mock('@/lib/api/orders', () => ({
  ordersApi: {
    create: jest.fn(),
    calculatePrice: jest.fn(),
  },
  ogosConfigApi: {
    getLocations: jest.fn(() => Promise.resolve([])),
    getMaterials: jest.fn(() => Promise.resolve([])),
  },
}))

describe('OrderForm', () => {
  const mockOnSubmit = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should render form with all required fields', () => {
    render(<OrderForm onSubmit={mockOnSubmit} />)
    
    expect(screen.getByLabelText(/location/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/quantity/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/street/i)).toBeInTheDocument()
  })

  it('should show organization select for B2B users', () => {
    render(<OrderForm onSubmit={mockOnSubmit} orderType="b2b" />)
    
    expect(screen.getByLabelText(/organization/i)).toBeInTheDocument()
  })

  it('should not show organization select for B2C users', () => {
    render(<OrderForm onSubmit={mockOnSubmit} orderType="b2c" />)
    
    expect(screen.queryByLabelText(/organization/i)).not.toBeInTheDocument()
  })

  it('should validate required fields', async () => {
    const user = userEvent.setup()
    render(<OrderForm onSubmit={mockOnSubmit} />)
    
    const submitButton = screen.getByRole('button', { name: /submit/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      // Check for labels with data-error attribute (indicating validation error)
      const errorLabels = document.querySelectorAll('label[data-error="true"]')
      
      // Should have at least one validation error
      expect(errorLabels.length).toBeGreaterThan(0)
    }, { timeout: 3000 })
  })

  it('should validate quantity is positive', async () => {
    const user = userEvent.setup()
    render(<OrderForm onSubmit={mockOnSubmit} />)
    
    const quantityInput = screen.getByLabelText(/quantity/i)
    await user.clear(quantityInput)
    await user.type(quantityInput, '-1')
    
    // Also fill location to avoid that error
    const locationInput = screen.getByLabelText(/location/i)
    await user.type(locationInput, 'NL001')
    
    const submitButton = screen.getByRole('button', { name: /submit/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      const errorMessages = screen.getAllByText(/.*/).map(el => el.textContent || '').join(' ')
      const hasQuantityError = errorMessages.toLowerCase().includes('quantity') && 
        (errorMessages.toLowerCase().includes('at least') || errorMessages.toLowerCase().includes('minimum'))
      expect(hasQuantityError).toBeTruthy()
    }, { timeout: 3000 })
  })

  it('should validate PDF is uploaded before submission', async () => {
    const user = userEvent.setup()
    render(<OrderForm onSubmit={mockOnSubmit} />)
    
    // Fill required fields
    const locationInput = screen.getByLabelText(/location/i)
    await user.type(locationInput, 'NL001')
    
    const quantityInput = screen.getByLabelText(/quantity/i)
    await user.type(quantityInput, '100')
    
    const nameInput = screen.getByLabelText(/name/i)
    await user.type(nameInput, 'John Doe')
    
    const streetInput = screen.getByLabelText(/street/i)
    await user.type(streetInput, '123 Main St')
    
    const cityInput = screen.getByLabelText(/city/i)
    await user.type(cityInput, 'Amsterdam')
    
    const postalInput = screen.getByLabelText(/postal.*code/i)
    await user.type(postalInput, '1000AA')
    
    const submitButton = screen.getByRole('button', { name: /submit/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByTestId('pdf-error')).toBeInTheDocument()
      expect(screen.getByText(/pdf.*required/i)).toBeInTheDocument()
    }, { timeout: 3000 })
  })

  it('should call onSubmit with form data when valid', async () => {
    const user = userEvent.setup()
    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' })
    
    render(<OrderForm onSubmit={mockOnSubmit} />)
    
    // Fill form
    const locationInput = screen.getByLabelText(/location/i)
    await user.type(locationInput, 'NL001')
    
    const quantityInput = screen.getByLabelText(/quantity/i)
    await user.type(quantityInput, '100')
    
    const nameInput = screen.getByLabelText(/name/i)
    await user.type(nameInput, 'John Doe')
    
    const streetInput = screen.getByLabelText(/street/i)
    await user.type(streetInput, '123 Main St')
    
    const cityInput = screen.getByLabelText(/city/i)
    await user.type(cityInput, 'Amsterdam')
    
    const postalInput = screen.getByLabelText(/postal.*code/i)
    await user.type(postalInput, '1000AA')
    
    // Upload PDF - find the file input in PDFUpload component
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement
    await user.upload(fileInput, file)
    
    // Wait for file to be set
    await waitFor(() => {
      expect(screen.getByText(/test\.pdf/i)).toBeInTheDocument()
    })
    
    // Submit
    const submitButton = screen.getByRole('button', { name: /submit/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          specifications: expect.objectContaining({
            location_code: 'NL001',
            quantity: 100,
          }),
          shipping_address: expect.objectContaining({
            name: 'John Doe',
            street: '123 Main St',
            city: 'Amsterdam',
            postal_code: '1000AA',
          }),
        })
      )
    })
  })

  it('should show loading state during submission', async () => {
    const user = userEvent.setup()
    let resolvePromise: () => void
    const promise = new Promise<void>(resolve => {
      resolvePromise = resolve
    })
    mockOnSubmit.mockImplementation(() => promise)
    
    render(<OrderForm onSubmit={mockOnSubmit} />)
    
    // Fill minimal required fields
    const locationInput = screen.getByLabelText(/location/i)
    await user.type(locationInput, 'NL001')
    
    const quantityInput = screen.getByLabelText(/quantity/i)
    await user.type(quantityInput, '100')
    
    const nameInput = screen.getByLabelText(/name/i)
    await user.type(nameInput, 'John Doe')
    
    const streetInput = screen.getByLabelText(/street/i)
    await user.type(streetInput, '123 Main St')
    
    const cityInput = screen.getByLabelText(/city/i)
    await user.type(cityInput, 'Amsterdam')
    
    const postalInput = screen.getByLabelText(/postal.*code/i)
    await user.type(postalInput, '1000AA')
    
    // Upload PDF
    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' })
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement
    await user.upload(fileInput, file)
    
    await waitFor(() => {
      expect(screen.getByText(/test\.pdf/i)).toBeInTheDocument()
    })
    
    const submitButton = screen.getByRole('button', { name: /submit/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(/submitting/i)).toBeInTheDocument()
    }, { timeout: 2000 })
    
    // Resolve promise
    resolvePromise!()
    await promise
  })

  it('should show error message on submission failure', async () => {
    const user = userEvent.setup()
    mockOnSubmit.mockRejectedValue(new Error('Submission failed'))
    
    render(<OrderForm onSubmit={mockOnSubmit} />)
    
    // Fill form
    const locationInput = screen.getByLabelText(/location/i)
    await user.type(locationInput, 'NL001')
    
    const quantityInput = screen.getByLabelText(/quantity/i)
    await user.type(quantityInput, '100')
    
    const nameInput = screen.getByLabelText(/name/i)
    await user.type(nameInput, 'John Doe')
    
    const streetInput = screen.getByLabelText(/street/i)
    await user.type(streetInput, '123 Main St')
    
    const cityInput = screen.getByLabelText(/city/i)
    await user.type(cityInput, 'Amsterdam')
    
    const postalInput = screen.getByLabelText(/postal.*code/i)
    await user.type(postalInput, '1000AA')
    
    // Upload PDF
    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' })
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement
    await user.upload(fileInput, file)
    
    await waitFor(() => {
      expect(screen.getByText(/test\.pdf/i)).toBeInTheDocument()
    })
    
    const submitButton = screen.getByRole('button', { name: /submit/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(/submission.*failed/i)).toBeInTheDocument()
    }, { timeout: 3000 })
  })
})

