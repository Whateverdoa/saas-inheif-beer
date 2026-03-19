'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Card } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Upload, X, File } from 'lucide-react'

interface PDFUploadProps {
  onFileSelect: (file: File) => void
  isUploading?: boolean
  uploadProgress?: number
  maxSize?: number // in bytes
}

const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB default

export function PDFUpload({
  onFileSelect,
  isUploading = false,
  uploadProgress = 0,
  maxSize = MAX_FILE_SIZE,
}: PDFUploadProps) {
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      setError(null)

      if (rejectedFiles.length > 0) {
        const rejection = rejectedFiles[0]
        if (rejection.errors.some((e: any) => e.code === 'file-too-large')) {
          setError('File is too large. Maximum size is 50MB.')
        } else if (rejection.errors.some((e: any) => e.code === 'file-invalid-type')) {
          setError('Only PDF files are allowed.')
        } else {
          setError('File upload failed. Please try again.')
        }
        return
      }

      if (acceptedFiles.length > 0) {
        const pdfFile = acceptedFiles[0]
        setFile(pdfFile)
        onFileSelect(pdfFile)
      }
    },
    [onFileSelect]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxSize,
    maxFiles: 1,
    disabled: isUploading,
  })

  const removeFile = () => {
    setFile(null)
    setError(null)
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  const rootProps = getRootProps()
  const inputProps = getInputProps()

  return (
    <div className="space-y-4">
      <Card
        {...(rootProps as any)}
        className={`border-2 border-dashed transition-colors cursor-pointer ${
          isDragActive
            ? 'border-primary bg-primary/5'
            : 'border-muted-foreground/25 hover:border-primary/50'
        } ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <div className="flex flex-col items-center justify-center p-8 text-center">
          <input {...inputProps} data-testid="file-input" disabled={isUploading} />
          <Upload className="h-12 w-12 mb-4 text-muted-foreground" />
          {isDragActive ? (
            <p className="text-lg font-medium">Drop PDF here...</p>
          ) : (
            <>
              <p className="text-lg font-medium mb-2">
                Drag & drop PDF here, or click to select
              </p>
              <p className="text-sm text-muted-foreground">
                Maximum file size: {formatFileSize(maxSize)}
              </p>
            </>
          )}
        </div>
      </Card>

      {error && (
        <div className="text-sm text-destructive bg-destructive/10 p-3 rounded-md">
          {error}
        </div>
      )}

      {file && (
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <File className="h-5 w-5 text-primary" />
              <div>
                <p className="font-medium">{file.name}</p>
                <p className="text-sm text-muted-foreground">
                  {formatFileSize(file.size)}
                </p>
              </div>
            </div>
            {!isUploading && (
              <Button
                variant="ghost"
                size="icon"
                onClick={removeFile}
                aria-label="Remove file"
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        </Card>
      )}

      {isUploading && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span>Uploading...</span>
            <span>{uploadProgress}%</span>
          </div>
          <Progress value={uploadProgress} className="h-2" />
        </div>
      )}
    </div>
  )
}

