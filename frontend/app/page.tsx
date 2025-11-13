"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";

export default function UploadPage() {
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [jobId, setJobId] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState(false);
  let API_URL = process.env.NEXT_PUBLIC_API_URL;
  if(!API_URL){
    API_URL="http://localhost:8000";
  }

  const fileRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const handleUpload = async () => {
    const file = fileRef.current?.files?.[0];
    if (!file) return alert("Please select a CSV file");

    const form = new FormData();
    form.append("file", file);

    setLoading(true);
    setStatus("Uploading...");
    setProgress(0);
    setUploadError(false);

    try {
      const res = await axios.post(`${API_URL}/upload`, form, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (event) => {
          if (event.total) {
            // Upload is phase 1, scale 0-50%
            const percent = Math.round((event.loaded * 10) / event.total);
            setProgress(percent);
            setStatus(`Uploading... ${percent}%`);
          }
        },
      });

      const { job_id } = res.data;
      setJobId(job_id);
      setStatus("Upload complete! Processing CSV...");
      pollJobStatus(job_id);
    } catch (err: any) {
      console.error(err);
      setStatus("Upload failed. Please try again.");
      setUploadError(true);
    } finally {
      setLoading(false);
    }
  };

  const pollJobStatus = (job_id: string) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_URL}/job_status/${job_id}`);
        const data = await res.json();

        // Processing is phase 2, scale 10-100%
        const percent = Math.round(10 + (data.progress / 2));
        setProgress(percent);
        setStatus(data.message);

        if (data.status === "completed" || data.status === "failed") {
          clearInterval(interval);
          if (data.status === "failed") setUploadError(true);
        }
      } catch (err) {
        console.error(err);
        clearInterval(interval);
        setStatus("Error fetching job status");
        setUploadError(true);
      }
    }, 10000);
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-gray-50 px-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow p-6">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4 text-center">
          Upload Products CSV
        </h2>

        <input
          type="file"
          accept=".csv"
          ref={fileRef}
          className="w-full text-sm text-gray-700 border border-gray-300 rounded-lg p-2 mb-4 cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-400"
        />

        <button
          onClick={handleUpload}
          disabled={loading}
          className={`w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition duration-150 ${
            loading ? "opacity-70 cursor-not-allowed" : ""
          }`}
        >
          {loading && (
            <svg
              className="animate-spin h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
              />
            </svg>
          )}
          {loading ? "Uploading..." : "Upload"}
        </button>

        {progress > 0 && (
          <div className="w-full bg-gray-200 rounded-full h-4 mt-4">
            <div
              className="bg-blue-600 h-4 rounded-full transition-all duration-200"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        )}

        {status && (
          <div
            className={`mt-4 text-center font-medium ${
              uploadError ? "text-red-500" : "text-green-600"
            }`}
          >
            {status} - {progress}%
          </div>
        )}

        {uploadError && (
          <button
            className="mt-4 w-full bg-yellow-500 hover:bg-yellow-600 text-white font-medium py-2 rounded-lg"
            onClick={handleUpload}
          >
            Retry
          </button>
        )}
      </div>

      <div className="w-full my-5 max-w-md flex justify-between">
        <button
          className="bg-blue-700 hover:bg-green-600 text-white font-medium py-2 px-4 mx-5 rounded-lg"
          onClick={() => router.push("/products")}
        >
          Go to Products
        </button>
        <button
          className="bg-blue-900 hover:bg-purple-600 text-white font-medium py-2 px-4 rounded-lg"
          onClick={() => router.push("/webhooks")}
        >
          Go to Webhooks
        </button>
      </div>
    </main>
  );
}
