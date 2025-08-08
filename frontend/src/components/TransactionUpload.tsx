"use client";

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle, CheckCircle, X, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { trackEvents } from '@/lib/analytics';

interface UploadProgress {
  status: 'idle' | 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  message: string;
  errors: string[];
  processedRows: number;
  totalRows: number;
}

interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  rowCount: number;
}

const TransactionUpload: React.FC = () => {
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>({
    status: 'idle',
    progress: 0,
    message: '',
    errors: [],
    processedRows: 0,
    totalRows: 0,
  });

  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploadProgress({
      status: 'uploading',
      progress: 0,
      message: 'Validating file format...',
      errors: [],
      processedRows: 0,
      totalRows: 0,
    });

    try {
      // Validate file type
      if (!file.name.endsWith('.csv') && !file.name.endsWith('.xlsx')) {
        throw new Error('Only CSV and Excel files are supported');
      }

      // Track upload event
      trackEvents.dataUploadStarted(file.name, file.size);

      // Simulate file validation and upload
      await simulateFileProcessing(file);

    } catch (error) {
      console.error('Upload error:', error);
      setUploadProgress({
        status: 'error',
        progress: 0,
        message: error instanceof Error ? error.message : 'Upload failed',
        errors: [error instanceof Error ? error.message : 'Unknown error'],
        processedRows: 0,
        totalRows: 0,
      });

      trackEvents.errorOccurred('upload_error', error instanceof Error ? error.message : 'Unknown error', {
        file_name: file.name,
        file_size: file.size,
      });
    }
  }, []);

  const simulateFileProcessing = async (file: File) => {
    // Simulate validation
    setUploadProgress(prev => ({ ...prev, progress: 20, message: 'Validating data structure...' }));
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Simulate data processing
    setUploadProgress(prev => ({ ...prev, progress: 50, message: 'Processing transaction data...' }));
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Simulate database insertion
    setUploadProgress(prev => ({ ...prev, progress: 80, message: 'Saving to database...' }));
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Complete
    setUploadProgress({
      status: 'completed',
      progress: 100,
      message: 'Upload completed successfully!',
      errors: [],
      processedRows: 1250,
      totalRows: 1250,
    });

    // Set validation result
    setValidationResult({
      isValid: true,
      errors: [],
      warnings: ['3 rows had missing location data', '1 row had invalid price format'],
      rowCount: 1250,
    });

    trackEvents.dataUploadCompleted(file.name, 'dld_transactions');
  };

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
    },
    multiple: false,
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  const resetUpload = () => {
    setUploadProgress({
      status: 'idle',
      progress: 0,
      message: '',
      errors: [],
      processedRows: 0,
      totalRows: 0,
    });
    setValidationResult(null);
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            DLD Transaction Upload
          </CardTitle>
          <CardDescription>
            Upload Dubai Land Department transaction data for analysis and insights.
            Supports CSV and Excel files up to 10MB.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Upload Area */}
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
              ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
              ${isDragReject ? 'border-red-500 bg-red-50' : ''}
              ${uploadProgress.status === 'uploading' || uploadProgress.status === 'processing' ? 'pointer-events-none opacity-50' : ''}
            `}
          >
            <input {...getInputProps()} />
            <div className="space-y-4">
              <Upload className="h-12 w-12 mx-auto text-gray-400" />
              <div>
                <p className="text-lg font-medium">
                  {isDragActive ? 'Drop the file here' : 'Drag & drop a file here, or click to select'}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  Supports CSV, XLSX, XLS files (max 10MB)
                </p>
              </div>
            </div>
          </div>

          {/* Progress Indicator */}
          {uploadProgress.status !== 'idle' && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">
                  {uploadProgress.message}
                </span>
                <Badge variant={uploadProgress.status === 'completed' ? 'default' : 'secondary'}>
                  {uploadProgress.status === 'uploading' && <Loader2 className="h-3 w-3 animate-spin mr-1" />}
                  {uploadProgress.status === 'completed' && <CheckCircle className="h-3 w-3 mr-1" />}
                  {uploadProgress.status === 'error' && <AlertCircle className="h-3 w-3 mr-1" />}
                  {uploadProgress.status}
                </Badge>
              </div>
              <Progress value={uploadProgress.progress} className="h-2" />
              {uploadProgress.processedRows > 0 && (
                <p className="text-xs text-gray-500">
                  Processed {uploadProgress.processedRows} of {uploadProgress.totalRows} rows
                </p>
              )}
            </div>
          )}

          {/* Error Display */}
          {uploadProgress.errors.length > 0 && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                <ul className="list-disc list-inside space-y-1">
                  {uploadProgress.errors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </AlertDescription>
            </Alert>
          )}

          {/* Validation Results */}
          {validationResult && (
            <div className="space-y-3">
              <Separator />
              <div className="space-y-2">
                <h4 className="font-medium">Validation Results</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Total Rows:</span> {validationResult.rowCount}
                  </div>
                  <div>
                    <span className="font-medium">Status:</span>
                    <Badge variant={validationResult.isValid ? 'default' : 'destructive'} className="ml-2">
                      {validationResult.isValid ? 'Valid' : 'Invalid'}
                    </Badge>
                  </div>
                </div>
                
                {validationResult.warnings.length > 0 && (
                  <Alert>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                      <p className="font-medium mb-1">Warnings:</p>
                      <ul className="list-disc list-inside space-y-1">
                        {validationResult.warnings.map((warning, index) => (
                          <li key={index}>{warning}</li>
                        ))}
                      </ul>
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-2">
            {uploadProgress.status === 'completed' && (
              <Button onClick={resetUpload} variant="outline">
                <X className="h-4 w-4 mr-2" />
                Upload Another File
              </Button>
            )}
            {uploadProgress.status === 'error' && (
              <Button onClick={resetUpload} variant="outline">
                Try Again
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Instructions */}
      <Card>
        <CardHeader>
          <CardTitle>File Requirements</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium mb-2">Required Columns</h4>
              <ul className="text-sm space-y-1 text-gray-600">
                <li>• Transaction ID</li>
                <li>• Property Type</li>
                <li>• Location</li>
                <li>• Transaction Date</li>
                <li>• Price (AED)</li>
                <li>• Area (sq ft)</li>
                <li>• Developer Name</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">File Format</h4>
              <ul className="text-sm space-y-1 text-gray-600">
                <li>• CSV, XLSX, or XLS format</li>
                <li>• Maximum file size: 10MB</li>
                <li>• UTF-8 encoding recommended</li>
                <li>• Headers in first row</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TransactionUpload; 