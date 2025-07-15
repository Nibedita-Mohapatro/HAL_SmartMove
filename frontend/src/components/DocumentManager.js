import React, { useState, useEffect } from 'react';
import FileUpload from './FileUpload';

const DocumentManager = ({ entityType, entityId, onClose }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDocuments();
  }, [entityType, entityId]);

  const fetchDocuments = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/documents/${entityType}/${entityId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDocuments(data.documents || []);
      } else {
        // For demo purposes, use mock data
        setDocuments(getMockDocuments());
      }
    } catch (error) {
      console.error('Error fetching documents:', error);
      setDocuments(getMockDocuments());
    } finally {
      setLoading(false);
    }
  };

  const getMockDocuments = () => {
    return [
      {
        id: 1,
        name: 'Insurance_Certificate.pdf',
        type: 'application/pdf',
        size: 245760,
        uploaded_at: '2024-07-10T10:30:00',
        uploaded_by: 'HAL001'
      },
      {
        id: 2,
        name: 'Maintenance_Report.docx',
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        size: 156432,
        uploaded_at: '2024-07-08T14:15:00',
        uploaded_by: 'HAL002'
      }
    ];
  };

  const handleUpload = async (formData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/documents/${entityType}/${entityId}/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setDocuments([...documents, ...result.documents]);
        return { success: true, message: 'Files uploaded successfully' };
      } else {
        // For demo purposes, simulate successful upload
        const mockDoc = {
          id: documents.length + 1,
          name: 'uploaded_file.pdf',
          type: 'application/pdf',
          size: 123456,
          uploaded_at: new Date().toISOString(),
          uploaded_by: 'HAL001'
        };
        setDocuments([...documents, mockDoc]);
        return { success: true, message: 'File uploaded successfully (demo)' };
      }
    } catch (error) {
      console.error('Upload error:', error);
      return { success: false, message: 'Upload failed' };
    }
  };

  const handleDelete = async (documentId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/documents/${documentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setDocuments(documents.filter(doc => doc.id !== documentId));
      } else {
        // For demo purposes, simulate successful deletion
        setDocuments(documents.filter(doc => doc.id !== documentId));
      }
    } catch (error) {
      console.error('Delete error:', error);
      setError('Failed to delete document');
    }
  };

  const handleDownload = async (documentId, fileName) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/documents/${documentId}/download`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        alert('Download not available in demo mode');
      }
    } catch (error) {
      console.error('Download error:', error);
      alert('Download failed');
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (type) => {
    if (type.includes('pdf')) return '📄';
    if (type.includes('word') || type.includes('document')) return '📝';
    if (type.includes('image')) return '🖼️';
    if (type.includes('excel') || type.includes('spreadsheet')) return '📊';
    return '📎';
  };

  const getEntityTitle = () => {
    switch (entityType) {
      case 'request':
        return 'Transport Request Documents';
      case 'vehicle':
        return 'Vehicle Documents';
      case 'driver':
        return 'Driver Documents';
      default:
        return 'Documents';
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
        <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
          <div className="flex items-center justify-center h-32">
            <div className="text-lg">Loading documents...</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-medium text-gray-900">{getEntityTitle()}</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            &times;
          </button>
        </div>

        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-md p-3">
            <div className="text-red-800 text-sm">{error}</div>
          </div>
        )}

        {/* File Upload */}
        <div className="mb-6">
          <h4 className="text-md font-medium text-gray-900 mb-3">Upload New Document</h4>
          <FileUpload
            onUpload={handleUpload}
            acceptedTypes=".pdf,.doc,.docx,.jpg,.jpeg,.png,.xlsx,.xls"
            maxSize={10 * 1024 * 1024} // 10MB
            multiple={true}
          />
        </div>

        {/* Documents List */}
        <div>
          <h4 className="text-md font-medium text-gray-900 mb-3">
            Existing Documents ({documents.length})
          </h4>
          
          {documents.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No documents uploaded yet
            </div>
          ) : (
            <div className="space-y-2">
              {documents.map((doc) => (
                <div key={doc.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-md hover:bg-gray-50">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{getFileIcon(doc.type)}</span>
                    <div>
                      <div className="text-sm font-medium text-gray-900">{doc.name}</div>
                      <div className="text-xs text-gray-500">
                        {formatFileSize(doc.size)} • Uploaded {new Date(doc.uploaded_at).toLocaleDateString()} by {doc.uploaded_by}
                      </div>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleDownload(doc.id, doc.name)}
                      className="text-hal-blue hover:text-hal-navy text-sm"
                    >
                      Download
                    </button>
                    <button
                      onClick={() => handleDelete(doc.id)}
                      className="text-red-600 hover:text-red-900 text-sm"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Close Button */}
        <div className="flex justify-end pt-6 mt-6 border-t">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentManager;
