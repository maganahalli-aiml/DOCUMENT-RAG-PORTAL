import React, { useState } from 'react';
import { PaperAirplaneIcon, DocumentIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import FileUpload from '../components/FileUpload';
import { apiService, UploadResponse, ChatResponse } from '../services/api';

interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

const SingleDocumentChat: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const handleFileSelect = async (selectedFile: File) => {
    setFile(selectedFile);
    setUploading(true);
    setUploadStatus('idle');
    
    try {
      const response: UploadResponse = await apiService.uploadAndIndex(selectedFile);
      
      if (response.status === 'success') {
        setSessionId(response.session_id);
        setUploadStatus('success');
        setMessages([{
          id: Date.now().toString(),
          type: 'system',
          content: `✅ Document "${selectedFile.name}" uploaded and indexed successfully! You can now ask questions about it.`,
          timestamp: new Date(),
        }]);
      } else {
        setUploadStatus('error');
        setMessages([{
          id: Date.now().toString(),
          type: 'system',
          content: `❌ Failed to upload document: ${response.message}`,
          timestamp: new Date(),
        }]);
      }
    } catch (error) {
      setUploadStatus('error');
      setMessages([{
        id: Date.now().toString(),
        type: 'system',
        content: `❌ Error uploading document: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
      }]);
    } finally {
      setUploading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!currentMessage.trim() || !sessionId || loading) return;

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
      const response: ChatResponse = await apiService.chatWithDocument(userMessage.content, sessionId);
      
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

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Single Document Chat</h1>
        <p className="text-gray-600">Upload a document and have an intelligent conversation about its content</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <div className="card space-y-4">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <DocumentIcon className="h-6 w-6 mr-2" />
            Document Upload
          </h2>
          
          <FileUpload
            onFileSelect={handleFileSelect}
            disabled={uploading}
          />

          {uploading && (
            <div className="flex items-center justify-center p-4">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-500 mr-3"></div>
              <span className="text-gray-600">Processing document...</span>
            </div>
          )}

          {file && (
            <div className={`p-4 rounded-lg border ${
              uploadStatus === 'success' 
                ? 'bg-green-50 border-green-200' 
                : uploadStatus === 'error'
                ? 'bg-red-50 border-red-200'
                : 'bg-gray-50 border-gray-200'
            }`}>
              <div className="flex items-center space-x-3">
                <DocumentIcon className="h-8 w-8 text-gray-400" />
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{file.name}</p>
                  <p className="text-sm text-gray-500">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                {uploadStatus === 'success' && (
                  <div className="text-green-600">✅</div>
                )}
                {uploadStatus === 'error' && (
                  <ExclamationTriangleIcon className="h-6 w-6 text-red-500" />
                )}
              </div>
            </div>
          )}
        </div>

        {/* Chat Section */}
        <div className="card space-y-4">
          <h2 className="text-xl font-semibold text-gray-900">Chat Interface</h2>
          
          {/* Messages */}
          <div className="h-96 overflow-y-auto border border-gray-200 rounded-lg p-4 space-y-4 bg-gray-50">
            {messages.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <p>Upload a document to start chatting!</p>
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
                    <p className="text-sm">{message.content}</p>
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
                    <span className="text-sm text-gray-500">AI is thinking...</span>
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
              placeholder={sessionId ? "Ask a question about your document..." : "Upload a document first"}
              disabled={!sessionId || loading}
              className="flex-1 input-field resize-none"
              rows={2}
            />
            <button
              onClick={handleSendMessage}
              disabled={!currentMessage.trim() || !sessionId || loading}
              className="btn-primary flex-shrink-0 flex items-center justify-center w-12 h-12 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <PaperAirplaneIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SingleDocumentChat;
