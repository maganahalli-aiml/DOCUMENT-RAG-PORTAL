import React, { useState } from 'react';
import { PaperAirplaneIcon, DocumentIcon, ExclamationTriangleIcon, TrashIcon } from '@heroicons/react/24/outline';
import FileUpload from '../components/FileUpload';
import { apiService, UploadResponse, ChatResponse } from '../services/api';

interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

interface UploadedFile {
  file: File;
  sessionId: string;
  status: 'uploading' | 'success' | 'error';
  errorMessage?: string;
}

const MultiDocumentChat: React.FC = () => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [globalSessionId] = useState<string>(`multi_session_${Date.now()}`);

  const handleFileSelect = async (selectedFile: File) => {
    await processFiles([selectedFile]);
  };

  const handleFilesSelect = async (selectedFiles: File[]) => {
    await processFiles(selectedFiles);
  };

  const processFiles = async (files: File[]) => {
    // Add all files to the list with uploading status
    const newFiles: UploadedFile[] = files.map(file => ({
      file,
      sessionId: globalSessionId,
      status: 'uploading'
    }));
    
    setUploadedFiles(prev => [...prev, ...newFiles]);
    
    // Process each file individually
    for (const selectedFile of files) {
      try {
        const response: UploadResponse = await apiService.uploadAndIndex(selectedFile, globalSessionId);
        
        if (response.status === 'success') {
          // Update file status to success
          setUploadedFiles(prev => 
            prev.map(f => 
              f.file.name === selectedFile.name 
                ? { ...f, status: 'success' as const }
                : f
            )
          );
          
          // Add success message
          setMessages(prev => [...prev, {
            id: Date.now().toString(),
            type: 'system',
            content: `✅ Document "${selectedFile.name}" uploaded and indexed successfully!`,
            timestamp: new Date(),
          }]);
        } else {
          // Update file status to error
          setUploadedFiles(prev => 
            prev.map(f => 
              f.file.name === selectedFile.name 
                ? { ...f, status: 'error' as const, errorMessage: response.message }
                : f
            )
          );
          
          setMessages(prev => [...prev, {
            id: Date.now().toString(),
            type: 'system',
            content: `❌ Failed to upload "${selectedFile.name}": ${response.message}`,
            timestamp: new Date(),
          }]);
        }
      } catch (error) {
        // Update file status to error
        setUploadedFiles(prev => 
          prev.map(f => 
            f.file.name === selectedFile.name 
              ? { ...f, status: 'error' as const, errorMessage: error instanceof Error ? error.message : 'Unknown error' }
              : f
          )
        );
        
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          type: 'system',
          content: `❌ Error uploading "${selectedFile.name}": ${error instanceof Error ? error.message : 'Unknown error'}`,
          timestamp: new Date(),
        }]);
      }
    }
    
    // Add summary message if multiple files were selected
    if (files.length > 1) {
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        type: 'system',
        content: `📁 Processing completed for ${files.length} files.`,
        timestamp: new Date(),
      }]);
    }
  };

  const handleRemoveFile = (fileName: string) => {
    setUploadedFiles(prev => prev.filter(f => f.file.name !== fileName));
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      type: 'system',
      content: `🗑️ Removed "${fileName}" from the session.`,
      timestamp: new Date(),
    }]);
  };

  const handleSendMessage = async () => {
    if (!currentMessage.trim() || loading) return;
    
    const successfulFiles = uploadedFiles.filter(f => f.status === 'success');
    if (successfulFiles.length === 0) {
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        type: 'system',
        content: '⚠️ Please upload at least one document successfully before asking questions.',
        timestamp: new Date(),
      }]);
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: currentMessage.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setLoading(true);

    try {
      const response: ChatResponse = await apiService.chatWithDocument(userMessage.content, globalSessionId);
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.answer || 'No response received from the AI.',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'system',
        content: `❌ Error: ${error instanceof Error ? error.message : 'Failed to get response'}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const successfulFiles = uploadedFiles.filter(f => f.status === 'success');

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Multi-Document Chat</h1>
        <p className="text-gray-600">Upload multiple documents and have intelligent conversations across all of them</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Section */}
        <div className="lg:col-span-1 space-y-4">
          <div className="card space-y-4">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center">
              <DocumentIcon className="h-6 w-6 mr-2" />
              Document Upload
            </h2>
            
            <FileUpload
              onFileSelect={handleFileSelect}
              onFilesSelect={handleFilesSelect}
              multiple={true}
              disabled={false}
            />

            {/* Uploaded Files List */}
            {uploadedFiles.length > 0 && (
              <div className="space-y-2">
                <h3 className="text-sm font-medium text-gray-700">Uploaded Documents ({uploadedFiles.length})</h3>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {uploadedFiles.map((uploadedFile, index) => (
                    <div
                      key={`${uploadedFile.file.name}-${index}`}
                      className={`p-3 rounded-lg border text-sm ${
                        uploadedFile.status === 'success' 
                          ? 'bg-green-50 border-green-200' 
                          : uploadedFile.status === 'error'
                          ? 'bg-red-50 border-red-200'
                          : 'bg-blue-50 border-blue-200'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2 flex-1 min-w-0">
                          <DocumentIcon className="h-4 w-4 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <p className="font-medium truncate">{uploadedFile.file.name}</p>
                            <p className="text-xs text-gray-500">
                              {(uploadedFile.file.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {uploadedFile.status === 'uploading' && (
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                          )}
                          {uploadedFile.status === 'success' && (
                            <div className="text-green-600">✅</div>
                          )}
                          {uploadedFile.status === 'error' && (
                            <ExclamationTriangleIcon className="h-4 w-4 text-red-500" />
                          )}
                          <button
                            onClick={() => handleRemoveFile(uploadedFile.file.name)}
                            className="text-gray-400 hover:text-red-500 transition-colors"
                          >
                            <TrashIcon className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                      {uploadedFile.status === 'error' && uploadedFile.errorMessage && (
                        <p className="text-xs text-red-600 mt-1">{uploadedFile.errorMessage}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Status Summary */}
            {successfulFiles.length > 0 && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-800">
                  ✅ {successfulFiles.length} document{successfulFiles.length !== 1 ? 's' : ''} ready for chat
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Chat Section */}
        <div className="lg:col-span-2">
          <div className="card space-y-4">
            <h2 className="text-xl font-semibold text-gray-900">Multi-Document Chat</h2>
            
            {/* Messages */}
            <div className="h-96 overflow-y-auto border border-gray-200 rounded-lg p-4 space-y-4 bg-gray-50">
              {messages.length === 0 ? (
                <div className="text-center text-gray-500 py-8">
                  <p>Upload documents to start chatting across multiple sources!</p>
                  <p className="text-sm mt-2">You can ask questions that span multiple documents.</p>
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        message.type === 'user'
                          ? 'bg-primary-500 text-white'
                          : message.type === 'system'
                          ? 'bg-yellow-100 text-yellow-800 border border-yellow-200'
                          : 'bg-white text-gray-900 border border-gray-200'
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      <p className={`text-xs mt-1 ${
                        message.type === 'user' ? 'text-primary-100' : 'text-gray-500'
                      }`}>
                        {message.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))
              )}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-white text-gray-900 border border-gray-200 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <div className="animate-pulse flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                      </div>
                      <span className="text-sm text-gray-500">AI is thinking across documents...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Input */}
            <div className="flex space-x-2">
              <textarea
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={successfulFiles.length > 0 ? "Ask a question about your documents..." : "Upload documents first"}
                disabled={successfulFiles.length === 0 || loading}
                className="flex-1 input-field resize-none"
                rows={2}
              />
              <button
                onClick={handleSendMessage}
                disabled={!currentMessage.trim() || successfulFiles.length === 0 || loading}
                className="btn-primary flex-shrink-0 flex items-center justify-center w-12 h-12 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <PaperAirplaneIcon className="h-5 w-5" />
              </button>
            </div>

            {/* Help Text */}
            {successfulFiles.length > 0 && (
              <div className="text-xs text-gray-500 space-y-1">
                <p><strong>💡 Try asking:</strong></p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>"Compare the main points from all documents"</li>
                  <li>"What are the common themes across these documents?"</li>
                  <li>"Summarize the key differences between documents"</li>
                  <li>"Find contradictions or conflicting information"</li>
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MultiDocumentChat;
