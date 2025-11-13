"use client";
import { useState, useRef } from "react";
import { useRouter } from "next/navigation";

export default function UploadPage() {
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  async function handleUpload() {
    const file = fileRef.current?.files?.[0];
    if (!file) return alert("Please select a CSV file");

    const form = new FormData();
    form.append("file", file);

    setLoading(true);
    setStatus("Uploading...");

    try {
      const res = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: form,
      });
      if (!res.ok) throw new Error("Upload failed");

      setStatus("Upload successful!");
      router.push("/products"); // redirect to products page
    } catch (err: any) {
      console.error(err);
      setStatus(err.message || "Upload failed");
    } finally {
      setLoading(false);
    }
  }

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

        {status && (
          <div
            className={`mt-4 text-center font-medium ${
              status.toLowerCase().includes("failed") ? "text-red-500" : "text-green-600"
            }`}
          >
            {status}
          </div>
        )}
      </div>
    </main>
  );
}
