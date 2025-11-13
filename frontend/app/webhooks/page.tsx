"use client";
import { useEffect, useState } from "react";

type Webhook = {
    id: number;
    url: string;
    event_types: string[];
    active: boolean;
};
type WebhookForm = {
    id?: number; // optional for new webhooks
    url: string;
    event_types: string[];
    active: boolean;
};

export default function WebhookManagement() {
    const [webhooks, setWebhooks] = useState<Webhook[]>([]);
    const [loading, setLoading] = useState(false);
    const [modalOpen, setModalOpen] = useState(false);
    const [selectedWebhook, setSelectedWebhook] = useState<WebhookForm | null>(null);
    const [testingWebhookId, setTestingWebhookId] = useState<number | null>(null);
    const [testResult, setTestResult] = useState<{ status_code: number; response_time_ms: number } | null>(null);


    // Fetch webhooks from API
    const fetchWebhooks = async () => {
        setLoading(true);
        const res = await fetch("http://localhost:8000/webhooks"); // adjust base URL
        setWebhooks(await res.json());
        setLoading(false);
    };

    const testWebhook = async (id: number, url: string) => {
        setTestingWebhookId(id);
        setTestResult(null);
        try {
            const res = await fetch(`http://localhost:8000/webhooks/${id}/test`, { method: "POST" });
            const result = await res.json();
            setTestResult(result);

            alert(`Status: ${result.status_code}, Time: ${result.response_time_ms}ms`);
        } catch (err) {
            alert(`Test failed: ${err}`);
        } finally {
            setTestingWebhookId(null);
        }
    };


    // Delete webhook
    const deleteWebhook = async (id: number) => {
        if (!confirm("Are you sure you want to delete this webhook?")) return;
        setLoading(true);
        await fetch(`http://localhost:8000/webhooks/${id}`, { method: "DELETE" });
        fetchWebhooks();
    };

    useEffect(() => {
        fetchWebhooks();
    }, []);

    return (
        <div className="p-6">
            {testingWebhookId && (
                <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center">
                    <div className="bg-gray-900 text-white p-4 rounded flex flex-col items-center">
                        <div className="spinner-border animate-spin border-t-2 border-white rounded-full w-8 h-8 mb-2"></div>
                        <span>Testing webhook...</span>
                        {testResult && (
                            <div className="mt-2 text-sm">
                                Status: {testResult.status_code}, Time: {testResult.response_time_ms}ms
                            </div>
                        )}
                    </div>
                </div>
            )}

            <h2 className="text-xl font-semibold mb-4">Webhook Management</h2>

            <button
                className="mb-4 bg-gray-200 text-black px-3 py-1 rounded"
                onClick={() => {
                    setSelectedWebhook(null);
                    setModalOpen(true);
                }}
            >
                Add Webhook
            </button>


            {loading ? (
                <div>Loading...</div>
            ) : (
                <table className="w-full border border-gray-200 rounded">
                    <thead>
                        <tr className="bg-gray-700">
                            <th className="border px-2 py-1">URL</th>
                            <th className="border px-2 py-1">Events</th>
                            <th className="border px-2 py-1">Active</th>
                            <th className="border px-2 py-1">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {Array.isArray(webhooks) && webhooks.map((w) => (
                            <tr key={w.id}>
                                <td className="border px-2 py-1">{w.url}</td>
                                <td className="border px-2 py-1">{w.event_types.join(", ")}</td>
                                <td className="border px-2 py-1">{w.active ? "Yes" : "No"}</td>
                                <td className="border px-2 py-1 space-x-1">
                                    <button
                                        className="bg-gray-200 text-black px-2 py-0.5 rounded"
                                        onClick={() => {
                                            setSelectedWebhook(w);
                                            setModalOpen(true);
                                        }}
                                    >
                                        Edit
                                    </button>
                                    <button
                                        className="bg-gray-600 text-white px-2 py-0.5 rounded"
                                        onClick={() => testWebhook(w.id, w.url)}
                                    >
                                        Test
                                    </button>
                                    <button
                                        className="bg-red-500 text-white px-2 py-0.5 rounded"
                                        onClick={() => deleteWebhook(w.id)}
                                    >
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
            {/* Modal for Add/Edit Webhook */}
            {modalOpen && (
                <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center">
                    <div className="bg-gray-900 rounded p-4 w-96 text-white">
                        <h3 className="text-lg font-semibold mb-2">
                            {selectedWebhook ? "Edit" : "Add"} Webhook
                        </h3>

                        {/* URL input */}
                        <input
                            type="text"
                            placeholder="Webhook URL"
                            value={selectedWebhook?.url || ""}
                            onChange={(e) =>
                                setSelectedWebhook((prev) => ({
                                    ...(prev || { url: "", event_types: [], active: true }),
                                    url: e.target.value,
                                }))
                            }
                            className="w-full border p-1 mb-2 rounded text-white"
                        />

                        {/* Event types input */}
                        <input
                            type="text"
                            placeholder="Event types (comma-separated)"
                            value={selectedWebhook?.event_types.join(", ") || ""}
                            onChange={(e) =>
                                setSelectedWebhook((prev) => ({
                                    ...(prev || { url: "", event_types: [], active: true }),
                                    event_types: e.target.value
                                        .split(",")
                                        .map((s) => s.trim())
                                        .filter(Boolean), // remove empty strings
                                }))
                            }
                            className="w-full border p-1 mb-2 rounded text-white"
                        />

                        {/* Active checkbox */}
                        <div className="flex items-center gap-2 mb-2">
                            <input
                                type="checkbox"
                                checked={selectedWebhook?.active ?? true}
                                onChange={(e) =>
                                    setSelectedWebhook((prev) => ({
                                        ...(prev || { url: "", event_types: [], active: true }),
                                        active: e.target.checked,
                                    }))
                                }
                            />
                            <span>Active</span>
                        </div>

                        {/* Buttons */}
                        <div className="flex justify-end gap-2">
                            <button
                                className="px-3 py-1 bg-gray-500 rounded"
                                onClick={() => {
                                    setModalOpen(false);
                                    setSelectedWebhook(null);
                                }}
                            >
                                Cancel
                            </button>

                            <button
                                className="px-3 py-1 bg-gray-700 rounded"
                                onClick={async () => {
                                    if (!selectedWebhook) return;

                                    const backendUrl = "http://localhost:8000";
                                    const isEdit = Boolean(selectedWebhook.id);

                                    // Only include required fields for POST
                                    const payload = {
                                        url: selectedWebhook.url,
                                        event_types: selectedWebhook.event_types,
                                        active: selectedWebhook.active,
                                    };


                                    const method = isEdit ? "PUT" : "POST";
                                    const url = isEdit
                                        ? `${backendUrl}/webhooks/${selectedWebhook.id}`
                                        : `${backendUrl}/webhooks`;

                                    try {
                                        const res = await fetch(url, {
                                            method,
                                            headers: { "Content-Type": "application/json" },
                                            body: JSON.stringify(payload),
                                        });

                                        if (!res.ok) {
                                            const errorData = await res.json();
                                            alert(`Error: ${JSON.stringify(errorData)}`);
                                            return;
                                        }

                                        setModalOpen(false);
                                        setSelectedWebhook(null);
                                        fetchWebhooks();
                                    } catch (err) {
                                        alert(`Request failed: ${err}`);
                                    }
                                }}
                            >
                                Save
                            </button>
                        </div>
                    </div>
                </div>
            )}


        </div>
    );
}
