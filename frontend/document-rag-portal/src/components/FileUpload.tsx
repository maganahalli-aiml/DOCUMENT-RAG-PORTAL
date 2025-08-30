import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { CloudArrowUpIcon, DocumentIcon } from '@heroicons/react/24/outline';

interface FileUploadProps {
  onFileSelect?: (file: File) => void;
  onFilesSelect?: (files: File[]) => void;
  accept?: Record<string, string[]>;
  maxSize?: number;
  multiple?: boolean;
  disabled?: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  onFilesSelect,
  accept = {
    'text/plain': ['.txt'],
    'application/pdf': ['.pdf'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    'text/csv': ['.csv'],
    'text/markdown': ['.md'],
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    'application/vnd.ms-powerpoint': ['.ppt'],
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
  },
  maxSize = 200 * 1024 * 1024, // 200MB
  multiple = false,
  disabled = false,
}) => {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        if (multiple && onFilesSelect) {
          onFilesSelect(acceptedFiles);
        } else if (onFileSelect) {
          onFileSelect(acceptedFiles[0]);
        }
      }
    },
    [onFileSelect, onFilesSelect, multiple]
  );

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept,
    maxSize,
    multiple,
    disabled,
  });

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 ${
          isDragActive
            ? 'border-primary-500 bg-primary-50'
            : disabled
            ? 'border-gray-200 bg-gray-50 cursor-not-allowed'
            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
        }`}
      >
        <input {...getInputProps()} />
        <CloudArrowUpIcon className={`mx-auto h-16 w-16 mb-4 ${
          isDragActive
            ? 'text-primary-500'
            : disabled
            ? 'text-gray-300'
            : 'text-gray-400'
        }`} />
        <div className="space-y-2">
          {isDragActive ? (
            <p className="text-lg font-medium text-primary-600">
              Drop the {multiple ? 'files' : 'file'} here...
            </p>
          ) : (
            <>
              <p className="text-lg font-medium text-gray-900">
                {disabled 
                  ? 'Upload disabled' 
                  : multiple 
                  ? 'Drag & drop files here, or click to select multiple files'
                  : 'Drag & drop a file here, or click to select'
                }
              </p>
              <p className="text-sm text-gray-500">
                Supports: PDF, DOCX, TXT, CSV, MD, XLSX, PPT, PPTX (max {Math.round(maxSize / (1024 * 1024))}MB each)
              </p>
            </>
          )}
        </div>
      </div>

      {fileRejections.length > 0 && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <h4 className="text-sm font-medium text-red-800 mb-2">File upload errors:</h4>
          <ul className="text-sm text-red-600 space-y-1">
            {fileRejections.map(({ file, errors }, index) => (
              <li key={index} className="flex items-center space-x-2">
                <DocumentIcon className="h-4 w-4 flex-shrink-0" />
                <span>{file.name}:</span>
                <span>{errors.map(e => e.message).join(', ')}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
