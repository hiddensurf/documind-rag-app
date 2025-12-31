import { FileText, MessageSquare, Sparkles } from 'lucide-react';

export default function WelcomeScreen() {
  return (
    <div className="flex-1 flex items-center justify-center p-8">
      <div className="max-w-2xl text-center space-y-8">
        <div className="space-y-4">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
            Welcome to DocuMind
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400">
            Your AI-powered document assistant with advanced CAD analysis
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
            <div className="flex justify-center mb-4">
              <FileText className="w-12 h-12 text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">
              Upload Documents
            </h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              Upload PDFs, Word docs, CAD files (DXF/DWG), and more
            </p>
          </div>

          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
            <div className="flex justify-center mb-4">
              <MessageSquare className="w-12 h-12 text-green-600 dark:text-green-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">
              Ask Questions
            </h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              Get instant answers from your documents using AI
            </p>
          </div>

          <div className="p-6 bg-purple-50 dark:bg-purple-900/20 rounded-lg shadow-lg border-2 border-purple-500">
            <div className="flex justify-center mb-4">
              <Sparkles className="w-12 h-12 text-purple-600 dark:text-purple-400 animate-pulse" />
            </div>
            <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">
              Advanced CAD Analysis
            </h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              5-stage AI vision analysis for CAD drawings
            </p>
          </div>
        </div>

        <div className="mt-12 p-6 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <h3 className="text-lg font-semibold mb-3 text-gray-900 dark:text-white">
            🚀 Getting Started
          </h3>
          <ol className="text-left text-gray-700 dark:text-gray-300 space-y-2 max-w-md mx-auto">
            <li className="flex items-start gap-2">
              <span className="font-bold text-blue-600 dark:text-blue-400">1.</span>
              <span>Click the <strong>Documents</strong> tab in the sidebar</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold text-blue-600 dark:text-blue-400">2.</span>
              <span>Upload your documents (PDF, DOCX, DXF, etc.)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold text-blue-600 dark:text-blue-400">3.</span>
              <span>Click <strong>New Chat</strong> to start asking questions</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold text-purple-600 dark:text-purple-400">💡</span>
              <span>For CAD files: Enable <strong>Advanced Analysis</strong> for comprehensive insights!</span>
            </li>
          </ol>
        </div>
      </div>
    </div>
  );
}
