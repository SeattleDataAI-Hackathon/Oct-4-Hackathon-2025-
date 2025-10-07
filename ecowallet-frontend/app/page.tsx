"use client";

import React, { useState, useCallback, useRef, useEffect } from "react";

type Page = "dashboard" | "chat";

interface AnalysisResult {
  sustainabilityScore: number;
  potentialMonthlySavings: number;
  summary: string;
  suggestions: {
    original: string;
    alternative: string;
    reasoning: string;
  }[];
}

interface ChatMessage {
  role: "user" | "assistant" | "error";
  content: string;
}

interface HeaderProps {
  setPage: (page: Page) => void;
  page: Page;
}

interface FileUploaderProps {
  onUploadSuccess: (data: AnalysisResult[] | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

interface DashboardProps {
  results: AnalysisResult[] | null;
}

interface ChatBubbleProps {
  message: ChatMessage;
}

const LeafIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className="mr-2 h-5 w-5 text-green-500"
  >
    <path d="M7 20h10" />
    <path d="M10 20c5.5-2.5.8-6.4 3-10" />
    <path d="M12 20c5.5-2.5.8-6.4 3-10" />
    <path d="M14 20c5.5-2.5.8-6.4 3-10" />
    <path d="M10 20c-5.5-2.5-.8-6.4-3-10" />
    <path d="M12 20c-5.5-2.5-.8-6.4-3-10" />
    <path d="M14 20c-5.5-2.5-.8-6.4-3-10" />
    <path d="M12 10V4" />
    <path d="M12 4c0-2.2-1.8-4-4-4" />
    <path d="M12 4c0-2.2 1.8-4 4-4" />
  </svg>
);

const UploadIcon = () => (
  <svg
    className="w-12 h-12 mb-4 text-gray-400"
    aria-hidden="true"
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 20 16"
  >
    <path
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"
    />
  </svg>
);

const BotIcon = () => (
  <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
    AI
  </div>
);

const UserIcon = () => (
  <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
    U
  </div>
);

const Header = ({ setPage, page }: HeaderProps) => {
  const linkClasses = (p: Page) =>
    `cursor-pointer px-4 py-2 rounded-md text-sm font-medium transition-colors ${
      page === p
        ? "bg-green-600 text-white"
        : "text-gray-600 hover:bg-green-100"
    }`;
  return (
    <header className="bg-white/80 backdrop-blur-lg shadow-sm fixed top-0 left-0 right-0 z-10">
      <nav className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <LeafIcon />
            <span className="text-xl font-bold text-gray-800">EcoWallet</span>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setPage("dashboard")}
              className={linkClasses("dashboard")}
            >
              Dashboard
            </button>
            <button
              onClick={() => setPage("chat")}
              className={linkClasses("chat")}
            >
              Eco Assistant
            </button>
          </div>
        </div>
      </nav>
    </header>
  );
};

const FileUploader = ({
  onUploadSuccess,
  setLoading,
  setError,
}: FileUploaderProps) => {
  const [files, setFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState<boolean>(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const fileList = Array.from(e.target.files);
      setFiles(fileList);
    }
  };

  const handleDrag = useCallback(
    (e: React.DragEvent<HTMLDivElement>, state: boolean) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(state);
    },
    []
  );

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      handleDrag(e, false);
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const fileList = Array.from(e.dataTransfer.files);
        setFiles(fileList);
      }
    },
    [handleDrag]
  );

  const handleSubmit = async () => {
    if (files.length === 0) {
      setError("Please select at least one file first!");
      return;
    }

    setLoading(true);
    setError(null);
    onUploadSuccess(null);

    try {
      const formData = new FormData();

      files.forEach((file) => {
        formData.append("files", file);
      });
      formData.append("username", "Abhishek");

      const response = await fetch(
        "http://localhost:5001/api/analyze-receipt",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.error || `HTTP error! status: ${response.status}`
        );
      }

      const results: AnalysisResult[] = await response.json();
      onUploadSuccess(results);
      setFiles([]);
    } catch (error) {
      console.error("Error uploading files:", error);
      setError(
        error instanceof Error
          ? error.message
          : "Failed to analyze receipts. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-lg mx-auto">
      <div
        className={`relative flex flex-col items-center justify-center w-full p-8 border-2 border-dashed rounded-lg transition-colors ${
          isDragging
            ? "border-green-500 bg-green-50"
            : "border-gray-300 bg-gray-50"
        }`}
        onDragEnter={(e) => handleDrag(e, true)}
        onDragLeave={(e) => handleDrag(e, false)}
        onDragOver={(e) => handleDrag(e, true)}
        onDrop={handleDrop}
      >
        <UploadIcon />
        <p className="mb-2 text-sm text-gray-500">
          <span className="font-semibold">Click to upload</span> or drag and
          drop
        </p>
        <p className="text-xs text-gray-500">
          PNG, JPG or JPEG (MAX. 5MB each)
        </p>
        <p className="text-xs text-gray-400 mt-1">Multiple files supported</p>
        <input
          id="dropzone-file"
          type="file"
          multiple
          className="absolute top-0 left-0 w-full h-full opacity-0 cursor-pointer"
          onChange={handleFileChange}
          accept="image/png, image/jpeg"
        />
      </div>

      {files.length > 0 && (
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-600 mb-2">
            Selected {files.length} file{files.length > 1 ? "s" : ""}:
          </p>
          <div className="space-y-1">
            {files.map((file, index) => (
              <p key={index} className="text-xs text-gray-500">
                <span className="font-medium">{file.name}</span>
              </p>
            ))}
          </div>
        </div>
      )}

      <button
        onClick={handleSubmit}
        disabled={files.length === 0}
        className="mt-6 w-full bg-green-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
      >
        Analyze {files.length > 1 ? `${files.length} Receipts` : "Receipt"}
      </button>
    </div>
  );
};

const Dashboard = ({ results }: DashboardProps) => {
  if (!results || results.length === 0) return null;

  // Filter out error results for calculations
  const validResults = results.filter(
    (result) => !("error" in result && result.error)
  );
  const errorResults = results.filter(
    (result) => "error" in result && result.error
  );

  if (validResults.length === 0) {
    return (
      <div className="mt-8 w-full max-w-3xl mx-auto p-4 sm:p-6 bg-white rounded-xl shadow-lg animate-fade-in">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600 mb-4">
            Analysis Failed
          </h2>
          <p className="text-gray-600">
            Unable to analyze any of the uploaded receipts.
          </p>
        </div>
      </div>
    );
  }

  // Calculate overall statistics from valid results only
  const overallScore = Math.round(
    validResults.reduce((sum, result) => sum + result.sustainabilityScore, 0) /
      validResults.length
  );
  const totalSavings = validResults.reduce(
    (sum, result) => sum + result.potentialMonthlySavings,
    0
  );

  // Collect all suggestions from valid results
  const allSuggestions = validResults.flatMap((result) => result.suggestions);

  return (
    <div className="mt-8 w-full max-w-4xl mx-auto p-4 sm:p-6 bg-white rounded-xl shadow-lg animate-fade-in">
      <h2 className="text-2xl sm:text-3xl font-bold text-gray-800 mb-6 text-center">
        Your Analysis {results.length > 1 && `(${results.length} Receipts)`}
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="flex flex-col items-center justify-center p-6 bg-green-50 rounded-lg">
          <p className="text-lg font-medium text-green-800">
            Overall Sustainability Score
          </p>
          <p className="text-6xl font-bold text-green-600 my-2">
            {overallScore}
            <span className="text-3xl text-gray-500">/100</span>
          </p>
          <p className="text-gray-600 text-sm text-center">
            Average across {validResults.length} receipt
            {validResults.length > 1 ? "s" : ""}
            {errorResults.length > 0 && ` (${errorResults.length} failed)`}
          </p>
        </div>
        <div className="flex flex-col items-center justify-center p-6 bg-blue-50 rounded-lg">
          <p className="text-lg font-medium text-blue-800">
            Total Potential Monthly Savings
          </p>
          <p className="text-6xl font-bold text-blue-600 my-2">
            ${totalSavings.toFixed(2)}
          </p>
          <p className="text-gray-600 text-sm text-center">
            by making sustainable swaps
          </p>
        </div>
      </div>

      {results.length > 1 && (
        <div className="mb-6">
          <h3 className="text-xl font-semibold mb-4 text-gray-700">
            Individual Receipt Scores
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {results.map((result, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg ${
                  "error" in result
                    ? "bg-red-50 border border-red-200"
                    : "bg-gray-50"
                }`}
              >
                <p className="font-medium text-gray-800 mb-2">
                  Receipt #{index + 1}
                  {"error" in result && (
                    <span className="text-red-600 text-sm ml-2">(Failed)</span>
                  )}
                </p>
                {"error" in result ? (
                  <p className="text-sm text-red-600">{String(result.error)}</p>
                ) : (
                  <>
                    <p className="text-2xl font-bold text-green-600">
                      {result.sustainabilityScore}/100
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      ${result.potentialMonthlySavings.toFixed(2)} savings
                    </p>
                  </>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div>
        <h3 className="text-xl font-semibold mb-4 text-gray-700">
          Sustainable Swaps 🌿
        </h3>
        <div className="space-y-4">
          {allSuggestions.map((item, index) => (
            <div
              key={index}
              className="p-4 border border-gray-200 rounded-lg bg-white hover:shadow-md transition-shadow"
            >
              <p className="font-semibold text-gray-800">
                Instead of{" "}
                <span className="text-red-600 font-bold">{item.original}</span>,
                try{" "}
                <span className="text-green-700 font-bold">
                  {item.alternative}
                </span>
                .
              </p>
              <p className="text-sm text-gray-600 mt-1">{item.reasoning}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const ChatBubble = ({ message }: ChatBubbleProps) => {
  const isUser = message.role === "user";
  const isError = message.role === "error";

  const bubbleClasses = isUser
    ? "bg-blue-500 text-white self-end"
    : isError
    ? "bg-red-100 text-red-800 self-start"
    : "bg-gray-200 text-gray-800 self-start";

  const icon = isUser ? <UserIcon /> : <BotIcon />;
  const flexDirection = isUser ? "flex-row-reverse" : "flex-row";

  return (
    <div className={`flex items-start gap-3 my-2 ${flexDirection}`}>
      {icon}
      <div className={`max-w-xs md:max-w-md p-3 rounded-lg ${bubbleClasses}`}>
        <p className="text-sm">{message.content}</p>
      </div>
    </div>
  );
};

const Chatbot = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Hi! How can I help you be more sustainable today? Ask me things like 'Book a 10-mile cab ride' or 'Order a pizza'.",
    },
  ]);
  const [input, setInput] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // NOTE: You need to create the '/api/eco-suggestion' endpoint in your Python backend.
      const response = await fetch("localhost:5001/api/eco-suggestion", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: input }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.error || `HTTP error! status: ${response.status}`
        );
      }
      const data = await response.json(); // Assuming backend returns { suggestion: "..." }

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.suggestion },
      ]);
    } catch (error) {
      console.error("Chat error:", error);
      // Fallback to mock logic if the API fails, so the chatbot is still usable for demo.
      let assistantResponse =
        "Sorry, I couldn't connect to the backend. Please ensure it's running. As a demo, I can still answer some questions!";
      if (input.toLowerCase().includes("pizza")) {
        assistantResponse =
          "(Mock) Great choice! To make it eco-friendly, consider ordering from a local pizzeria that uses fresh, local ingredients to reduce food miles.";
      } else if (
        input.toLowerCase().includes("cab") ||
        input.toLowerCase().includes("ride")
      ) {
        assistantResponse =
          "(Mock) For a 10-mile ride, an electric vehicle (EV) taxi or rideshare is a fantastic option. If available, public transport would be even better.";
      }
      setMessages((prev) => [
        ...prev,
        { role: "error", content: assistantResponse },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)] w-full max-w-2xl mx-auto bg-white rounded-xl shadow-2xl">
      <div className="flex-1 p-4 overflow-y-auto">
        <div className="flex flex-col space-y-2">
          {messages.map((msg, index) => (
            <ChatBubble key={index} message={msg} />
          ))}
          {isLoading && (
            <div className="flex items-start gap-3 my-2 flex-row">
              <BotIcon />
              <div className="max-w-xs md:max-w-md p-3 rounded-lg bg-gray-200 text-gray-800 self-start">
                <div className="flex items-center space-x-1">
                  <span className="h-2 w-2 bg-gray-500 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                  <span className="h-2 w-2 bg-gray-500 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                  <span className="h-2 w-2 bg-gray-500 rounded-full animate-bounce"></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>
      <div className="p-4 border-t border-gray-200 bg-white rounded-b-xl">
        <form onSubmit={handleSubmit} className="flex items-center space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask for an eco-friendly tip..."
            className="flex-1 p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none"
            disabled={isLoading}
          />
          <button
            type="submit"
            className="bg-green-600 text-white p-2 rounded-lg hover:bg-green-700 disabled:bg-gray-400"
            disabled={isLoading}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="m22 2-7 20-4-9-9-4Z" />
              <path d="M22 2 11 13" />
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
};

export default function Home() {
  const [page, setPage] = useState<Page>("dashboard");
  const [analysisResults, setAnalysisResults] = useState<
    AnalysisResult[] | null
  >(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-gray-50 font-sans text-gray-900">
      <Header setPage={setPage} page={page} />
      <main className="pt-24 pb-12 px-4">
        {page === "dashboard" && (
          <div className="animate-fade-in">
            <div className="text-center mb-10">
              <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-800">
                Your Spending, Reimagined
              </h1>
              <p className="text-gray-600 mt-2 max-w-xl mx-auto">
                Upload a receipt to get your sustainability score and discover
                eco-friendly alternatives.
              </p>
            </div>

            <FileUploader
              onUploadSuccess={setAnalysisResults}
              setLoading={setLoading}
              setError={setError}
            />

            {error && (
              <p className="mt-6 text-center text-red-600 bg-red-100 p-3 rounded-lg">
                {error}
              </p>
            )}

            {loading && (
              <div className="mt-8 text-center">
                <div
                  role="status"
                  className="flex items-center justify-center space-x-2"
                >
                  <svg
                    aria-hidden="true"
                    className="w-8 h-8 text-gray-200 animate-spin fill-green-600"
                    viewBox="0 0 100 101"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                      fill="currentColor"
                    />
                    <path
                      d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0492C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                      fill="currentFill"
                    />
                  </svg>
                  <span className="text-lg font-medium text-gray-600">
                    Analyzing your receipt
                    {analysisResults && analysisResults.length > 1 ? "s" : ""}
                    ...
                  </span>
                </div>
              </div>
            )}

            <Dashboard results={analysisResults} />
          </div>
        )}

        {page === "chat" && (
          <div className="animate-fade-in">
            <div className="text-center mb-10">
              <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-800">
                Eco Assistant
              </h1>
              <p className="text-gray-600 mt-2 max-w-xl mx-auto">
                Your personal AI chatbot for quick sustainability tips and
                advice.
              </p>
            </div>
            <Chatbot />
          </div>
        )}
      </main>
    </div>
  );
}
