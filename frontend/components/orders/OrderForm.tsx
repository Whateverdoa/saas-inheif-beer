'use client'

import { useState, useEffect, useMemo } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Checkbox } from '@/components/ui/checkbox'
import { PDFUpload } from './PDFUpload'
import { pdfApi } from '@/lib/api/pdf'
import { priceApi } from '@/lib/api/price'
import type { OrderType, CreateOrderRequest, OrderLine, OrderSpecifications, ShippingAddress } from '@/lib/types/orders'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { File, X } from 'lucide-react'

const SUBSTRATE_OPTIONS = [
  { value: 'Glans Wit (P)', label: 'Glans Wit (P)', materialId: 1 },
  { value: 'Glans Wit (R)', label: 'Glans Wit (R)', materialId: 2 },
  { value: 'Mat Wit (P)', label: 'Mat Wit (P)', materialId: 3 },
  { value: 'Mat Wit (R)', label: 'Mat Wit (R)', materialId: 4 },
  { value: 'PP Mat Wit', label: 'PP Mat Wit', materialId: 5 },
  { value: 'PP Glans Wit', label: 'PP Glans Wit', materialId: 6 },
  { value: 'PP transparant', label: 'PP transparant', materialId: 7 },
  { value: 'Fluor Geel', label: 'Fluor Geel', materialId: 8 },
  { value: 'Fluor Rood', label: 'Fluor Rood', materialId: 9 },
  { value: 'Fluor Oranje', label: 'Fluor Oranje', materialId: 10 },
  { value: 'Fluor Groen', label: 'Fluor Groen', materialId: 11 },
  { value: 'Fluor Magenta', label: 'Fluor Magenta', materialId: 12 },
  { value: 'Kraft Bruin permanent', label: 'Kraft Bruin permanent', materialId: 13 },
  { value: 'Glans Zilver', label: 'Glans Zilver', materialId: 14 },
  { value: 'Antique White', label: 'Antique White', materialId: 15 },
  { value: 'Paperwise White', label: 'Paperwise White', materialId: 16 },
  { value: 'Paperwise Natural', label: 'Paperwise Natural', materialId: 17 },
  { value: 'Natureflex white', label: 'Natureflex white', materialId: 18 },
  { value: 'Natureflex transparant', label: 'Natureflex transparant', materialId: 19 },
  { value: 'Coverall permanent', label: 'Coverall permanent', materialId: 20 },
  { value: 'PP Holografisch', label: 'PP Holografisch', materialId: 65 },
  { value: 'Tintoretto Gesso', label: 'Tintoretto Gesso', materialId: 76 },
]

// Helper function to get material ID from substrate code
const getMaterialId = (substrateCode: string | undefined): number | undefined => {
  if (!substrateCode) return undefined
  const option = SUBSTRATE_OPTIONS.find(opt => opt.value === substrateCode)
  return option?.materialId
}

const LOCATION_OPTIONS = [
  { value: 'L02', label: 'L02' },
  { value: 'L03', label: 'L03' },
  { value: 'L04', label: 'L04' },
]

const CORE_DIAMETER_OPTIONS = [
  { value: 76, label: '76 mm' },
  { value: 40, label: '40 mm' },
  { value: 25, label: '25 mm' },
]

const SHAPE_OPTIONS = [
  { value: 'CIRCLE', label: 'Circle' },
  { value: 'RECTANGLE', label: 'Rectangle' },
  { value: 'CUSTOM', label: 'Custom' },
]

const SHIPPING_METHOD_OPTIONS = [
  { value: 'POSTNL_REGULAR', label: 'PostNL Regular', price: 4.95 },
  { value: 'POSTNL_EXPRESS', label: 'PostNL Express', price: 9.95 },
]

const DEFAULT_VENDOR = 'brons'

/**
 * Round radius according to special rules:
 * - Keep .5 values (1.5 stays 1.5)
 * - Round up if above .5 (1.6, 1.7, etc. round to 2)
 * - Values below .5 stay as is (1.4 stays 1.4, 1.0 stays 1.0)
 */
function roundRadius(value: number): number {
  const decimal = Math.abs(value % 1)
  const whole = Math.floor(value)
  
  // Handle floating point precision issues
  const roundedDecimal = Math.round(decimal * 10) / 10
  
  if (Math.abs(roundedDecimal - 0.5) < 0.01) {
    // Keep .5 values as is (1.5 stays 1.5)
    return whole + 0.5
  } else if (roundedDecimal > 0.5) {
    // Round up to next whole number (1.6, 1.7, etc. -> 2)
    return whole + 1
  } else {
    // Keep values below .5 as is (1.4 stays 1.4, 1.0 stays 1.0)
    return value
  }
}

const orderSchema = z.object({
  org_id: z.string().optional(),
  location_code: z.string().min(1, 'Location is required'),
  material_code: z.string().optional(),
  quantity: z.number().min(1, 'Quantity must be at least 1'),
  shape: z.string().optional(),
  core_size: z.string().optional(),
  product_type: z.string().optional(),
  shipping_method: z.string().optional().default('POSTNL_REGULAR'),
  // Additional fields for L02 labelsonrol/stickers
  width: z.number().positive().optional(),
  height: z.number().positive().optional(),
  radius: z.number().nonnegative().optional().default(2),
  premium_white: z.boolean().optional(),
  substrate: z.string().optional(),
  substrate_id: z.number().int().positive().optional(),
  winding: z.number().int().positive().optional(),
  laser_compatible: z.boolean().optional(),
  description: z.string().optional(),
  quantity_per_roll: z.number().int().nonnegative().optional(),
  core_diameter: z.number().int().positive().optional(),
  line_comment: z.string().optional(),
  shipping_name: z.string().min(1, 'Name is required'),
  shipping_street: z.string().min(1, 'Street is required'),
  shipping_city: z.string().min(1, 'City is required'),
  shipping_postal_code: z.string().min(1, 'Postal code is required'),
  shipping_country: z.string().default('NL'),
  shipping_phone: z.string().optional(),
})

type OrderFormValues = z.input<typeof orderSchema>

interface OrderFormProps {
  onSubmit: (data: CreateOrderRequest) => Promise<void>
  orderType?: OrderType
  orgId?: string
  accountShippingAddress?: ShippingAddress
}

interface PDFWithMetadata {
  file: File
  parsedData?: {
    width?: number
    height?: number
    radius?: number
    color_space?: string
    is_cmyk?: boolean
    warnings?: string[]
    validation_errors?: string[]
  }
  specifications: OrderSpecifications
  isParsing?: boolean
  parseError?: string
  price?: {
    price: number
    shipping_cost: number
    total: number
  }
  isCalculatingPrice?: boolean
}

export function OrderForm({
  onSubmit,
  orderType = 'b2c',
  orgId,
  accountShippingAddress,
}: OrderFormProps) {
  const [pdfFiles, setPdfFiles] = useState<PDFWithMetadata[]>([])
  const [isParsingPdf, setIsParsingPdf] = useState(false)
  const [isCalculatingPrice, setIsCalculatingPrice] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [pdfError, setPdfError] = useState<string | null>(null)
  const [calculatedPrice, setCalculatedPrice] = useState<{
    price: number
    shipping_cost: number
    total: number
    breakdown?: Record<string, number>
  } | null>(null)
  const [isAccepted, setIsAccepted] = useState(false)

  const form = useForm<OrderFormValues>({
    resolver: zodResolver(orderSchema),
    defaultValues: {
      shipping_country: 'NL',
      premium_white: false,
      laser_compatible: true,
      location_code: 'L02',
      core_diameter: 76,
      substrate: SUBSTRATE_OPTIONS[0]?.value || 'Glans Wit (P)',
      substrate_id: 1, // Default MaterialID for "Glans Wit (P)"
      winding: 2,
      quantity: 1000,
      shape: 'RECTANGLE',
      shipping_method: 'POSTNL_REGULAR',
      radius: 2, // Default 2mm for rectangles (90% of cases)
    },
  })

  const isB2BWithDerivedShipping = orderType === 'b2b' && !!accountShippingAddress

  useEffect(() => {
    if (!isB2BWithDerivedShipping || !accountShippingAddress) {
      return
    }

    const { name, street, city, postal_code, country, phone } = accountShippingAddress

    form.setValue('shipping_name', name)
    form.setValue('shipping_street', street)
    form.setValue('shipping_city', city)
    form.setValue('shipping_postal_code', postal_code)
    form.setValue('shipping_country', country || 'NL')
    form.setValue('shipping_phone', phone || '')
  }, [accountShippingAddress, form, isB2BWithDerivedShipping])

  // Parse PDFs when files are selected
  const handlePdfSelect = async (files: File[]) => {
    setPdfError(null)
    setCalculatedPrice(null)
    setIsAccepted(false)
    setError(null)

    if (files.length === 0) {
      setPdfFiles([])
      form.resetField('width')
      form.resetField('height')
      return
    }

    setIsParsingPdf(true)

    // Get form defaults for specifications
    const formDefaults = form.getValues()
    const defaultSpecs: OrderSpecifications = {
      location_code: formDefaults.location_code || 'L02',
      quantity: formDefaults.quantity || 1000,
      shape: formDefaults.shape || 'RECTANGLE',
      width: formDefaults.width,
      height: formDefaults.height,
      radius: formDefaults.radius || 0,
      premium_white: formDefaults.premium_white || false,
      substrate: formDefaults.substrate,
      substrate_id: formDefaults.substrate_id,
      winding: formDefaults.winding || 2,
      laser_compatible: formDefaults.laser_compatible ?? true,
      description: formDefaults.description,
      quantity_per_roll: formDefaults.quantity_per_roll,
      core_diameter: formDefaults.core_diameter || 76,
      line_comment: formDefaults.line_comment,
    }

    // Create initial entries for all files
    const newPdfFiles: PDFWithMetadata[] = files.map(file => ({
      file,
      specifications: { ...defaultSpecs },
      isParsing: true,
    }))
    setPdfFiles(newPdfFiles)

    // Parse each PDF individually
    const parsePromises = files.map(async (file, index) => {
      try {
        console.log(`Parsing PDF ${index + 1}/${files.length}: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`)
        
        // Parse PDF (timeout is handled in the API client)
        const result = await pdfApi.parse(file)
        
        console.log(`PDF ${index + 1} parsed successfully: ${file.name}`)
        
        if (!result || !result.ok) {
          return {
            index,
            error: result?.error || 'Failed to parse PDF',
            parsedData: undefined,
          }
        }

        // Extract parsed data
        const parsedData = {
          width: result.width,
          height: result.height,
          radius: result.radius,
          color_space: result.color_space,
          is_cmyk: result.is_cmyk,
          warnings: result.warnings,
          validation_errors: result.validation_errors,
        }

        // Create specifications with parsed values, using form defaults as fallback
        const specs: OrderSpecifications = {
          ...defaultSpecs,
          width: result.width || defaultSpecs.width,
          height: result.height || defaultSpecs.height,
          radius: result.radius !== undefined && result.radius !== null 
            ? roundRadius(result.radius) 
            : (defaultSpecs.shape === 'RECTANGLE' ? 2 : 0),
        }

        return {
          index,
          parsedData,
          specifications: specs,
          error: undefined,
        }
      } catch (err) {
        const error = err as Error & { errors?: string[]; validation_errors?: string[] }
        let errorMessage = error.message || 'Failed to parse PDF'
        
        if (error.errors && error.errors.length > 0) {
          errorMessage = `${errorMessage}: ${error.errors.join(', ')}`
        } else if (error.validation_errors && error.validation_errors.length > 0) {
          errorMessage = `${errorMessage}: ${error.validation_errors.join(', ')}`
        }
        
        return {
          index,
          error: errorMessage,
          parsedData: undefined,
        }
      }
    })

    // Wait for all parsing to complete (use allSettled so one failure doesn't stop others)
    const settledResults = await Promise.allSettled(parsePromises)
    const results = settledResults.map((settled, index) => {
      if (settled.status === 'fulfilled') {
        return settled.value
      } else {
        // Handle rejected promise
        console.error(`PDF ${index + 1} parsing failed:`, settled.reason)
        return {
          index,
          error: settled.reason?.message || 'Failed to parse PDF',
          parsedData: undefined,
        }
      }
    })

    // Update state with parsed results
    setPdfFiles(prev => prev.map((pdf, index) => {
      const result = results.find(r => r.index === index)
      if (!result) {
        return {
          ...pdf,
          isParsing: false,
        }
      }

      if (result.error) {
        return {
          ...pdf,
          isParsing: false,
          parseError: result.error,
        }
      }

      return {
        ...pdf,
        isParsing: false,
        parsedData: result.parsedData,
        specifications: ('specifications' in result && result.specifications) ? result.specifications : pdf.specifications,
      }
    }))

    // Set form values from first PDF if available
    const firstSuccess = results.find(r => !r.error && r.parsedData)
    if (firstSuccess && firstSuccess.parsedData) {
      if (firstSuccess.parsedData.width) {
        form.setValue('width', firstSuccess.parsedData.width)
      }
      if (firstSuccess.parsedData.height) {
        form.setValue('height', firstSuccess.parsedData.height)
      }
      if (firstSuccess.parsedData.radius !== undefined && firstSuccess.parsedData.radius !== null) {
        form.setValue('radius', roundRadius(firstSuccess.parsedData.radius))
      }
    }

    setIsParsingPdf(false)
    
    // Trigger price calculation after state updates (using updated pdfFiles)
    // We'll use a useEffect to handle this instead
  }

  const removePdfFile = (index: number) => {
    const newFiles = pdfFiles.filter((_, i) => i !== index)
    setPdfFiles(newFiles)
    // No need to re-parse automatically; parsing occurs when user adds files again
    if (newFiles.length === 0) {
      handlePdfSelect([])
    }
  }

  // Calculate price when form values change
  const calculatePrice = async () => {
    const formData = form.getValues()
    
    // If we have PDFs, calculate price per PDF and sum them
    if (pdfFiles.length > 0) {
      // Check if all PDFs have required data
      const validPdfs = pdfFiles.filter(pdf => 
        !pdf.isParsing && 
        !pdf.parseError && 
        pdf.parsedData?.width && 
        pdf.parsedData?.height && 
        pdf.specifications.quantity && 
        pdf.specifications.quantity > 0
      )

      if (validPdfs.length === 0) {
        setCalculatedPrice(null)
        return
      }

      setIsCalculatingPrice(true)
      setError(null)
      
      // Set calculating state for all PDFs
      setPdfFiles(prev => prev.map(pdf => ({ ...pdf, isCalculatingPrice: true })))

      try {
        // Calculate price for each PDF line
        // Map validPdfs to their indices in pdfFiles for matching
        const validPdfIndices = pdfFiles.map((pdf, idx) => {
          const isValid = !pdf.isParsing && 
            !pdf.parseError && 
            pdf.parsedData?.width && 
            pdf.parsedData?.height && 
            pdf.specifications.quantity && 
            pdf.specifications.quantity > 0
          return isValid ? idx : -1
        }).filter(idx => idx !== -1)

        const pricePromises = validPdfs.map(async (pdf, validIdx) => {
          const specs = pdf.specifications
          const parsed = pdf.parsedData!
          
          const result = await priceApi.calculate({
            width_mm: parsed.width!,
            height_mm: parsed.height!,
            quantity: specs.quantity!,
            substrate: specs.substrate || formData.substrate,
            vendor: DEFAULT_VENDOR,
            laminaat: 'none',
            soorten: 1,
            dekwit: specs.premium_white ?? formData.premium_white ?? false,
            rolls_specific_qty: specs.winding ?? formData.winding ?? 0,
            use_special_start: false,
          })
          
          return { pdfIndex: validPdfIndices[validIdx], pdfFileName: pdf.file.name, result }
        })

        const results = await Promise.all(pricePromises)
        
        // Check for errors first
        const hasError = results.some(r => !r.result.ok)
        if (hasError) {
          const errorResult = results.find(r => !r.result.ok)
          setError(errorResult?.result.error || 'Failed to calculate price for one or more PDFs')
          setCalculatedPrice(null)
          // Clear calculating state
          setPdfFiles(prev => prev.map(pdf => ({ ...pdf, isCalculatingPrice: false })))
          return
        }

        // Update each PDF with its individual price (without shipping - shipping is added once to total order)
        setPdfFiles(prev => prev.map((pdf, idx) => {
          const priceResult = results.find(r => r.pdfIndex === idx || r.pdfFileName === pdf.file.name)
          if (priceResult && priceResult.result.ok && priceResult.result.price !== undefined) {
            console.log(`Setting price for PDF ${idx} (${pdf.file.name}):`, {
              price: priceResult.result.price,
            })
            return {
              ...pdf,
              price: {
                price: priceResult.result.price,
                shipping_cost: 0, // No shipping per PDF - shipping is added once to total order
                total: priceResult.result.price, // Price without shipping
              },
              isCalculatingPrice: false,
            }
          } else {
            console.log(`No price result found for PDF ${idx} (${pdf.file.name})`, {
              priceResult: priceResult ? {
                hasResult: true,
                ok: priceResult.result.ok,
                hasPrice: priceResult.result.price !== undefined,
                price: priceResult.result.price,
              } : null,
              results: results.map(r => ({ index: r.pdfIndex, fileName: r.pdfFileName })),
            })
          }
          return { ...pdf, isCalculatingPrice: false }
        }))

        // Sum up all prices for total order price
        const totalPrice = results.reduce((sum, r) => sum + (r.result.price || 0), 0)
        const totalArea = results.reduce((sum, r) => sum + (r.result.total_area_m2 || 0), 0)
        
        // Calculate shipping cost based on selected shipping method (once per order)
        const orderShippingMethod = formData.shipping_method || 'POSTNL_REGULAR'
        const orderShippingOption = SHIPPING_METHOD_OPTIONS.find(opt => opt.value === orderShippingMethod)
        const shippingCost = orderShippingOption?.price || 4.95

        const total = totalPrice + shippingCost
        
        setCalculatedPrice({
          price: totalPrice,
          shipping_cost: shippingCost,
          total: total,
          breakdown: results.reduce((acc, r) => {
            // Merge breakdowns if available
            if (r.result.breakdown) {
              Object.entries(r.result.breakdown).forEach(([key, value]) => {
                acc[key] = (acc[key] || 0) + (value as number)
              })
            }
            return acc
          }, {} as Record<string, number>),
        })
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to calculate price')
        setCalculatedPrice(null)
      } finally {
        setIsCalculatingPrice(false)
      }
      return
    }

    // Fallback to single PDF calculation if no PDFs uploaded yet
    if (!formData.width || !formData.height || !formData.quantity) {
      setCalculatedPrice(null)
      return
    }

    setIsCalculatingPrice(true)
    setError(null)

    try {
      const result = await priceApi.calculate({
        width_mm: formData.width,
        height_mm: formData.height,
        quantity: formData.quantity,
        substrate: formData.substrate,
        vendor: DEFAULT_VENDOR,
        laminaat: 'none',
        soorten: 1,
        dekwit: formData.premium_white || false,
        rolls_specific_qty: formData.winding ?? 0,
        use_special_start: false,
      })
      
      if (!result.ok) {
        setError(result.error || 'Failed to calculate price')
        setCalculatedPrice(null)
        return
      }
      
      // Calculate shipping cost based on selected shipping method
      const shippingMethod = formData.shipping_method || 'POSTNL_REGULAR'
      const shippingOption = SHIPPING_METHOD_OPTIONS.find(opt => opt.value === shippingMethod)
      const shippingCost = shippingOption?.price || 4.95

      if (result.price !== undefined) {
        const total = result.price + shippingCost
        setCalculatedPrice({
          price: result.price,
          shipping_cost: shippingCost,
          total: total,
          breakdown: result.breakdown,
        })
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to calculate price')
      setCalculatedPrice(null)
    } finally {
      setIsCalculatingPrice(false)
    }
  }

  // Calculate price when relevant fields change
  // Watch shape changes and update radius default accordingly
  useEffect(() => {
    const subscription = form.watch((value, { name }) => {
      if (name === 'shape') {
        const shape = value.shape || 'RECTANGLE'
        const currentRadius = form.getValues('radius') || 0
        
        // Only update if radius is 0 (sharp rectangle) or if switching from rectangle to circle/custom
        if (shape === 'RECTANGLE' && currentRadius === 0) {
          form.setValue('radius', 2) // Set to 2mm default for rectangles
        } else if ((shape === 'CIRCLE' || shape === 'CUSTOM') && currentRadius > 0) {
          form.setValue('radius', 0) // Set to 0mm for circle/custom
        }
      }
    })
    
    return () => subscription.unsubscribe()
  }, [form])
  
  useEffect(() => {
    const subscription = form.watch((value, { name }) => {
      if (
        name &&
        [
          'quantity',
          'width',
          'height',
          'substrate',
          'premium_white',
          'laser_compatible',
          'winding',
          'shipping_method',
        ].includes(name)
      ) {
        calculatePrice()
      }
    })
    return () => subscription.unsubscribe()
  }, [pdfFiles]) // Re-run when PDFs change

  // Create stable dependency strings for PDF quantities and parsing status
  const pdfQuantitiesKey = useMemo(() => {
    return pdfFiles.map(p => `${p.file.name}-${p.specifications.quantity || 0}`).join('|')
  }, [pdfFiles])

  const pdfParsingStatusKey = useMemo(() => {
    return pdfFiles.map(p => `${p.isParsing}-${!!p.parsedData}-${!!p.parseError}`).join('|')
  }, [pdfFiles])

  // Recalculate price when PDF quantities change or when PDFs finish parsing
  useEffect(() => {
    if (pdfFiles.length > 0) {
      // Check if any PDFs are still parsing
      const stillParsing = pdfFiles.some(pdf => pdf.isParsing)
      if (stillParsing) {
        // Don't calculate yet, wait for parsing to complete
        return
      }

      // Only calculate if PDFs are parsed and have quantities
      const validPdfs = pdfFiles.filter(pdf => 
        !pdf.parseError && 
        pdf.parsedData?.width && 
        pdf.parsedData?.height && 
        pdf.specifications.quantity && 
        pdf.specifications.quantity > 0
      )
      
      console.log('Price calculation check:', {
        pdfFilesCount: pdfFiles.length,
        validPdfsCount: validPdfs.length,
        stillParsing,
        pdfs: pdfFiles.map(p => ({
          name: p.file.name,
          isParsing: p.isParsing,
          hasParsedData: !!p.parsedData,
          hasWidth: !!p.parsedData?.width,
          hasHeight: !!p.parsedData?.height,
          quantity: p.specifications.quantity,
          hasError: !!p.parseError,
        }))
      })
      
      if (validPdfs.length > 0) {
        // Use a small delay to debounce rapid changes
        const timer = setTimeout(() => {
          console.log('Triggering price calculation for', validPdfs.length, 'PDFs')
          calculatePrice()
        }, 500)
        return () => clearTimeout(timer)
      } else {
        // Clear price if no valid PDFs
        console.log('No valid PDFs for price calculation, clearing price')
        setCalculatedPrice(null)
      }
    } else {
      // Clear price if no PDFs
      setCalculatedPrice(null)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pdfQuantitiesKey, pdfParsingStatusKey, pdfFiles.length]) // Recalculate when quantities, parsing status, or count changes

  const handleAccept = async () => {
    const formData = form.getValues()
    const isValid = await form.trigger()
    if (!isValid) {
      return
    }
    
    if (pdfFiles.length === 0) {
      setPdfError('At least one PDF file is required')
      return
    }

    // Ensure all files have been parsed successfully before continuing
    const hasParsing = pdfFiles.some(pdf => pdf.isParsing)
    if (hasParsing) {
      setPdfError('Please wait for all PDFs to finish parsing')
      return
    }

    const hasParsingError = pdfFiles.some(pdf => pdf.parseError)
    if (hasParsingError) {
      setPdfError('One or more PDFs failed to parse. Remove or re-upload them before submitting.')
      return
    }

    // Check if all PDFs have quantities set
    const missingQuantities = pdfFiles.filter(pdf => !pdf.specifications.quantity || pdf.specifications.quantity < 1)
    if (missingQuantities.length > 0) {
      setPdfError(`Please set quantity for all PDFs. Missing quantity for: ${missingQuantities.map((_, i) => `PDF ${i + 1}`).join(', ')}`)
      return
    }

    if (!calculatedPrice) {
      await calculatePrice()
      return
    }

    setIsAccepted(true)
    setIsSubmitting(true)
    setError(null)
    setPdfError(null)

    try {
      // Convert PDF files to order lines
      const orderLines: OrderLine[] = pdfFiles.map(pdf => ({
        file: pdf.file,
        specifications: pdf.specifications,
        parsedData: pdf.parsedData,
      }))

      const orderData: CreateOrderRequest = {
        order_type: orderType,
        reference: `ORDER-${Date.now()}`,
        org_id: orderType === 'b2b' ? (orgId || formData.org_id) : undefined,
        order_lines: orderLines,
        shipping_address: {
          name: formData.shipping_name,
          street: formData.shipping_street,
          city: formData.shipping_city,
          postal_code: formData.shipping_postal_code,
          country: formData.shipping_country,
          phone: formData.shipping_phone,
        },
      }

      await onSubmit(orderData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Submission failed')
      setIsAccepted(false)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Form {...form}>
      <form className="space-y-6">
        {/* PDF Upload at the top */}
        <div className="space-y-2">
          <Label className="text-lg font-semibold">PDF Upload</Label>
          <PDFUpload 
            onFileSelect={handlePdfSelect} 
            isUploading={isParsingPdf || isSubmitting}
          />
          {pdfError && (
            <p className="text-sm text-destructive" data-testid="pdf-error">{pdfError}</p>
          )}
          {isParsingPdf && (
            <p className="text-sm text-muted-foreground">Parsing PDFs and extracting dimensions...</p>
          )}
        </div>

        {/* Display uploaded PDFs with their values */}
        {pdfFiles.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Label className="text-lg font-semibold">Uploaded PDFs ({pdfFiles.length})</Label>
              <div className="text-sm">
                <span className="text-muted-foreground">Total Quantity: </span>
                <span className="font-semibold text-lg">
                  {pdfFiles.reduce((sum, pdf) => sum + (pdf.specifications.quantity || 0), 0).toLocaleString()}
                </span>
              </div>
            </div>
            <div className="space-y-3">
              {pdfFiles.map((pdf, index) => (
                <Card key={index} className="p-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <File className="h-5 w-5 text-primary" />
                        <div>
                          <p className="font-medium">{pdf.file.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {(pdf.file.size / 1024).toFixed(2)} KB
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {pdf.isParsing && (
                          <Badge variant="secondary">Parsing...</Badge>
                        )}
                        {pdf.parseError && (
                          <Badge variant="destructive">Error</Badge>
                        )}
                        {!pdf.isParsing && !pdf.parseError && pdf.parsedData && (
                          <Badge variant="default">Ready</Badge>
                        )}
                        {!isSubmitting && (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => removePdfFile(index)}
                            aria-label={`Remove ${pdf.file.name}`}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </div>

                    {pdf.parseError && (
                      <div className="text-sm text-destructive bg-destructive/10 p-2 rounded">
                        {pdf.parseError}
                      </div>
                    )}

                    {pdf.parsedData && !pdf.parseError && (
                      <div className="space-y-4">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <p className="text-muted-foreground">Format</p>
                            <p className="font-medium">
                              {pdf.parsedData.width?.toFixed(2) || 'N/A'} × {pdf.parsedData.height?.toFixed(2) || 'N/A'} mm
                            </p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Radius</p>
                            <p className="font-medium">{pdf.parsedData.radius?.toFixed(2) ?? 'N/A'} mm</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Color Space</p>
                            <p className="font-medium">{pdf.parsedData.color_space || 'N/A'}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Price</p>
                            {pdf.isCalculatingPrice ? (
                              <p className="font-medium text-muted-foreground">Calculating...</p>
                            ) : pdf.price ? (
                              <p className="font-medium text-green-600">€{pdf.price.price.toFixed(2)}</p>
                            ) : (
                              <p className="font-medium text-muted-foreground">-</p>
                            )}
                          </div>
                        </div>
                        
                        {/* Per-PDF Quantity Input */}
                        <div className="border-t pt-3">
                        <Label htmlFor={`quantity-${index}`} className="text-sm font-medium">
                            Units for this PDF
                          </Label>
                          <Input
                            id={`quantity-${index}`}
                            type="number"
                            min="1"
                            value={pdf.specifications.quantity || ''}
                            onChange={(e) => {
                              const newQuantity = parseInt(e.target.value) || 0
                              setPdfFiles(prev => prev.map((p, i) => 
                                i === index 
                                  ? { ...p, specifications: { ...p.specifications, quantity: newQuantity }, isCalculatingPrice: true }
                                  : p
                              ))
                              // Recalculate price when quantity changes
                              setTimeout(() => calculatePrice(), 100)
                            }}
                            className="mt-1"
                            placeholder="Enter quantity"
                          />
                          <p className="text-xs text-muted-foreground mt-1">
                            Current: {pdf.specifications.quantity || 'Not set'}
                            {pdf.price && (
                              <span className="ml-2">
                                (€{pdf.price.price.toFixed(2)})
                              </span>
                            )}
                          </p>
                        </div>
                        {pdf.parsedData.warnings && pdf.parsedData.warnings.length > 0 && (
                          <div className="col-span-full">
                            <p className="text-muted-foreground">Warnings:</p>
                            <ul className="list-disc list-inside text-yellow-600">
                              {pdf.parsedData.warnings.map((warning, i) => (
                                <li key={i}>{warning}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {pdf.parsedData.validation_errors && pdf.parsedData.validation_errors.length > 0 && (
                          <div className="col-span-full">
                            <p className="text-muted-foreground">Validation Errors:</p>
                            <ul className="list-disc list-inside text-destructive">
                              {pdf.parsedData.validation_errors.map((error, i) => (
                                <li key={i}>{error}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

        {orderType === 'b2b' && (
          <FormField
            control={form.control}
            name="org_id"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Organization</FormLabel>
                <FormControl>
                  <Input value={field.value || ''} onChange={field.onChange} onBlur={field.onBlur} placeholder="Select organization" />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        )}

        <FormField
          control={form.control}
          name="location_code"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Location</FormLabel>
              <FormControl>
                <Select onValueChange={field.onChange} value={field.value || 'L02'}>
                  <SelectTrigger aria-label="Location">
                    <SelectValue placeholder="Select location" />
                  </SelectTrigger>
                  <SelectContent>
                    {LOCATION_OPTIONS.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Substrate dropdown before other product details */}
        <FormField
          control={form.control}
          name="substrate"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Substrate</FormLabel>
              <FormControl>
                <Select
                  onValueChange={(value) => {
                    field.onChange(value)
                    // Automatically set substrate_id when substrate changes
                    const materialId = getMaterialId(value)
                    if (materialId) {
                      form.setValue('substrate_id', materialId)
                    }
                  }}
                  value={field.value || undefined}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select substrate" />
                  </SelectTrigger>
                  <SelectContent>
                    {SUBSTRATE_OPTIONS.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Product Details */}
        <div className="space-y-4 border-t pt-4">
          <Label className="text-lg font-semibold">Product Details</Label>
          
          <div className="grid grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="width"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Width (mm)</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      step="0.1"
                      value={field.value ?? ''}
                      onChange={(e) => field.onChange(e.target.value ? parseFloat(e.target.value) : undefined)}
                      onBlur={field.onBlur}
                      placeholder="70.0"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="height"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Height (mm)</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      step="0.1"
                      value={field.value ?? ''}
                      onChange={(e) => field.onChange(e.target.value ? parseFloat(e.target.value) : undefined)}
                      onBlur={field.onBlur}
                      placeholder="50.0"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <FormField
            control={form.control}
            name="radius"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Radius (mm)</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    step="0.1"
                    value={field.value ?? ''}
                    onChange={(e) => {
                      const value = e.target.value ? parseFloat(e.target.value) : undefined
                      if (value !== undefined && value >= 0) {
                        // Store raw value while typing
                        field.onChange(value)
                      } else if (e.target.value === '') {
                        field.onChange(undefined)
                      }
                    }}
                    onBlur={(e) => {
                      const value = e.target.value ? parseFloat(e.target.value) : undefined
                      if (value !== undefined && value >= 0) {
                        const rounded = roundRadius(value)
                        field.onChange(rounded)
                      }
                    }}
                    placeholder="0"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="quantity"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Default units (for new PDFs)</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      value={field.value ?? ''}
                      onChange={(e) => {
                        const newQuantity = parseInt(e.target.value) || 0
                        field.onChange(newQuantity)
                        // Only update PDFs that are newly added (don't have a quantity set yet)
                        // Don't update existing PDFs that already have quantities
                      }}
                      onBlur={field.onBlur}
                      placeholder="1000"
                      aria-label="Quantity"
                    />
                  </FormControl>
                <p className="text-xs text-muted-foreground">
                  Default quantity applied when uploading new PDFs. Set individual quantities per PDF below. Total order quantity is the sum of all PDF quantities.
                </p>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="shape"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Shape</FormLabel>
                <FormControl>
                  <Select onValueChange={field.onChange} value={field.value || undefined}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select shape" />
                    </SelectTrigger>
                    <SelectContent>
                      {SHAPE_OPTIONS.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="grid grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="substrate_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Substrate ID</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      value={field.value ?? ''}
                      onChange={(e) => field.onChange(e.target.value ? parseInt(e.target.value) : undefined)}
                      onBlur={field.onBlur}
                      placeholder="20"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="winding"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Winding</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      value={field.value ?? ''}
                      onChange={(e) => field.onChange(e.target.value ? parseInt(e.target.value) : undefined)}
                      onBlur={field.onBlur}
                      placeholder="2"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="core_diameter"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Core Diameter (mm)</FormLabel>
                  <FormControl>
                    <Select 
                      onValueChange={(value) => field.onChange(parseInt(value))} 
                      value={field.value?.toString() || '76'}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select core diameter" />
                      </SelectTrigger>
                      <SelectContent>
                        {CORE_DIAMETER_OPTIONS.map((option) => (
                          <SelectItem key={option.value} value={option.value.toString()}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="quantity_per_roll"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Units per Roll</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      value={field.value ?? ''}
                      onChange={(e) => field.onChange(e.target.value ? parseInt(e.target.value) : undefined)}
                      onBlur={field.onBlur}
                      placeholder="0"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <FormField
            control={form.control}
            name="description"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Description</FormLabel>
                <FormControl>
                  <Input value={field.value || ''} onChange={field.onChange} onBlur={field.onBlur} placeholder="F4G9972ED2" />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="line_comment"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Line Comment</FormLabel>
                <FormControl>
                  <Input
                    value={field.value || ''}
                    onChange={field.onChange}
                    onBlur={field.onBlur}
                    placeholder="Order reference"
                    autoComplete="off"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="flex items-center gap-6">
            <FormField
              control={form.control}
              name="premium_white"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center space-x-3 space-y-0">
                  <FormControl>
                    <Checkbox
                      checked={field.value || false}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                  <FormLabel className="!mt-0 cursor-pointer">Premium White</FormLabel>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="laser_compatible"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center space-x-3 space-y-0">
                  <FormControl>
                    <Checkbox
                      checked={field.value || false}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                  <FormLabel className="!mt-0 cursor-pointer">Laser Compatible</FormLabel>
                </FormItem>
              )}
            />
          </div>
        </div>

        {/* Shipping Address */}
        <div className="space-y-4 border-t pt-4">
          <Label className="text-lg font-semibold">Shipping Address</Label>
          {isB2BWithDerivedShipping && (
            <p className="text-sm text-muted-foreground">
              Shipping address is pulled from your B2B account and cannot be edited here.
            </p>
          )}
          
          <FormField
            control={form.control}
            name="shipping_method"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Shipping Method</FormLabel>
                <FormControl>
                  <Select
                    onValueChange={(value) => {
                      field.onChange(value)
                      // Recalculate price when shipping method changes
                      calculatePrice()
                    }}
                    value={field.value || 'POSTNL_REGULAR'}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select shipping method" />
                    </SelectTrigger>
                    <SelectContent>
                      {SHIPPING_METHOD_OPTIONS.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label} - €{option.price.toFixed(2)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
              control={form.control}
              name="shipping_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Name</FormLabel>
                  <FormControl>
                    <Input
                      value={field.value || ''}
                      onChange={field.onChange}
                      onBlur={field.onBlur}
                      placeholder="Full name"
                      autoComplete="name"
                      readOnly={isB2BWithDerivedShipping}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

          <FormField
            control={form.control}
            name="shipping_street"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Street</FormLabel>
                <FormControl>
                  <Input
                    value={field.value || ''}
                    onChange={field.onChange}
                    onBlur={field.onBlur}
                    placeholder="Street address"
                    autoComplete="street-address"
                    readOnly={isB2BWithDerivedShipping}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="grid grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="shipping_city"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>City</FormLabel>
                  <FormControl>
                    <Input
                      value={field.value || ''}
                      onChange={field.onChange}
                      onBlur={field.onBlur}
                      placeholder="City"
                      autoComplete="address-level2"
                      readOnly={isB2BWithDerivedShipping}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="shipping_postal_code"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Postal Code</FormLabel>
                  <FormControl>
                    <Input
                      value={field.value || ''}
                      onChange={field.onChange}
                      onBlur={field.onBlur}
                      placeholder="1234AB"
                      autoComplete="postal-code"
                      readOnly={isB2BWithDerivedShipping}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <FormField
            control={form.control}
            name="shipping_phone"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Phone (Optional)</FormLabel>
                <FormControl>
                  <Input
                    value={field.value || ''}
                    onChange={field.onChange}
                    onBlur={field.onBlur}
                    placeholder="+31 6 12345678"
                    autoComplete="tel"
                    readOnly={isB2BWithDerivedShipping}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* Price Calculation */}
        {isCalculatingPrice && (
          <div className="text-sm text-muted-foreground">Calculating price...</div>
        )}

        {calculatedPrice && (
          <div className="rounded-lg border bg-muted/50 p-4 space-y-2">
            <h3 className="font-semibold">Price Calculation</h3>
            <div className="flex justify-between">
              <span>Unit Price:</span>
              <span>€{calculatedPrice.price.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span>Shipping:</span>
              <span>€{calculatedPrice.shipping_cost.toFixed(2)}</span>
            </div>
            <div className="flex justify-between border-t pt-2 font-semibold">
              <span>Total:</span>
              <span>€{calculatedPrice.total.toFixed(2)}</span>
            </div>
          </div>
        )}

        {error && (
          <div className="text-sm text-destructive bg-destructive/10 p-3 rounded-md">
            {error}
          </div>
        )}

        {/* Accept Button */}
        <Button 
          type="button"
          onClick={handleAccept}
          disabled={isSubmitting || isCalculatingPrice || pdfFiles.length === 0}
          className="w-full"
        >
          {isSubmitting ? 'Submitting Order...' : isCalculatingPrice ? 'Calculating...' : 'Accept & Submit Order'}
        </Button>
      </form>
    </Form>
  )
}
