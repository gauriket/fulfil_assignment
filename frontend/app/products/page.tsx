"use client";
import { useEffect, useState } from "react";

type Product = {
    id: number;
    sku: string;
    name?: string;
    description?: string;
    price?: number;
    active: boolean;
};

export default function ProductManagement() {
    const [products, setProducts] = useState<Product[]>([]);
    const [loading, setLoading] = useState(false);
    const [filters, setFilters] = useState({ sku: "", name: "", description: "", active: "" });
    const [page, setPage] = useState(0);
    const [selectedProduct, setSelectedProduct] = useState<Partial<Product> | null>(null);
    const [modalOpen, setModalOpen] = useState(false);
    const [isEdit, setIsEdit] = useState(false);
    const [bulkDeleting, setBulkDeleting] = useState(false);


    const fetchProducts = async () => {
        setLoading(true);
        const params = new URLSearchParams();
        Object.entries(filters).forEach(([k, v]) => v && params.append(k, v));
        params.append("skip", (page * 20).toString());
        params.append("limit", "20");

        const res = await fetch(`http://localhost:8000/products?${params.toString()}`);
        const data = await res.json();
        setProducts(data);
        setLoading(false);
    };

    useEffect(() => {
        fetchProducts();
    }, [page, filters]);

    // Update the delete function to use SKU
    const deleteProduct = async (sku: string) => {
        if (!confirm("Are you sure you want to delete this product?")) return;
        await fetch(`http://localhost:8000/products/${sku}`, { method: "DELETE" });
        fetchProducts();
    };

    const saveProduct = async (product: Partial<Product> & { id?: number }) => {
        if (isEdit) {
            await fetch(`http://localhost:8000/products/${product.sku}`, {
                method: "PUT",
                body: JSON.stringify(product),
                headers: { "Content-Type": "application/json" },
            });
        } else {
            await fetch(`http://localhost:8000/products`, {
                method: "POST",
                body: JSON.stringify(product),
                headers: { "Content-Type": "application/json" },
            });
        }
        setModalOpen(false);
        fetchProducts();
    };

    const bulkDeleteProducts = async () => {
        if (!confirm("Are you sure? This cannot be undone.")) return;

        try {
            setBulkDeleting(true); // show spinner
            const res = await fetch(`http://localhost:8000/products`, {
                method: "DELETE",
            });

            if (res.ok) {
                alert("All products deleted successfully!");
            } else {
                const error = await res.text();
                alert("Failed to delete products: " + error);
            }

            fetchProducts(); // refresh list
        } catch (err) {
            alert("Error deleting products: " + err);
        } finally {
            setBulkDeleting(false); // hide spinner
        }
    };

    return (
        <div className="p-6">
            <h2 className="text-xl font-semibold mb-4">Product Management</h2>

            {/* Filters */}
            <div className="flex gap-2 mb-4">
                <input
                    type="text"
                    placeholder="SKU"
                    value={filters.sku}
                    onChange={(e) => setFilters({ ...filters, sku: e.target.value })}
                    className="border p-1 rounded"
                />
                <input
                    type="text"
                    placeholder="Name"
                    value={filters.name}
                    onChange={(e) => setFilters({ ...filters, name: e.target.value })}
                    className="border p-1 rounded"
                />
                <input
                    type="text"
                    placeholder="Description"
                    value={filters.description}
                    onChange={(e) => setFilters({ ...filters, description: e.target.value })}
                    className="border p-1 rounded"
                />
                <select
                    value={filters.active}
                    onChange={(e) => setFilters({ ...filters, active: e.target.value })}
                    className="border p-1 rounded"
                >
                    <option value="">All</option>
                    <option value="true">Active</option>
                    <option value="false">Inactive</option>
                </select>
                <button
                    onClick={() => {
                        setSelectedProduct({
                            id: 0,
                            sku: "",
                            name: "",
                            description: "",
                            price: 0,
                            active: true,
                        });
                        setIsEdit(false);
                        setModalOpen(true);
                    }}
                    className="ml-auto bg-gray-600 text-white px-3 py-1 rounded"
                >
                    Add Product
                </button>
                {/* ...existing filter inputs */}
                <button
                    onClick={bulkDeleteProducts}
                    className="ml-auto bg-red-600 text-white px-3 py-1 rounded flex items-center gap-2"
                    disabled={bulkDeleting}
                >
                    {bulkDeleting && <span className="loader-border"></span>} {/* simple spinner */}
                    Delete All
                </button>


            </div>

            {/* Table */}
            {loading ? (
                <div>Loading...</div>
            ) : (
                <table className="w-full border border-gray-200 rounded">
                    <thead>
                        <tr className="bg-gray-700">
                            <th className="border px-2 py-1">SKU</th>
                            <th className="border px-2 py-1">Name</th>
                            <th className="border px-2 py-1">Description</th>
                            <th className="border px-2 py-1">Price</th>
                            <th className="border px-2 py-1">Active</th>
                            <th className="border px-2 py-1">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {products.map((p) => (
                            <tr key={p.id}>
                                <td className="border px-2 py-1">{p.sku}</td>
                                <td className="border px-2 py-1">{p.name}</td>
                                <td className="border px-2 py-1">{p.description}</td>
                                <td className="border px-2 py-1">{p.price}</td>
                                <td className="border px-2 py-1">{p.active ? "Yes" : "No"}</td>
                                <td className="border px-2 py-1 space-x-1">
                                    <button
                                        onClick={() => {
                                            setSelectedProduct(p); // the product to edit
                                            setIsEdit(true);
                                            setModalOpen(true);
                                        }}
                                        className="bg-gray-200 text-black px-2 py-0.5 rounded"
                                    >
                                        Edit
                                    </button>

                                    <button
                                        className="bg-gray-500 text-white px-2 py-0.5 rounded"
                                        onClick={() => deleteProduct(p.sku)}
                                    >
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}

            {/* Pagination */}
            <div className="mt-4 flex justify-between">
                <button
                    disabled={page === 0}
                    onClick={() => setPage(page - 1)}
                    className="px-3 py-1 border rounded disabled:opacity-50"
                >
                    Previous
                </button>
                <button onClick={() => setPage(page + 1)} className="px-3 py-1 border rounded">
                    Next
                </button>
            </div>

            {/* Modal for Add/Edit */}
            {/* Modal for Add/Edit */}
            {modalOpen && (
                <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center">
                    <div className="bg-gray-900 rounded p-4 w-96">
                        <h3 className="text-lg font-semibold mb-2">
                            {isEdit ? "Edit" : "Add"} Product
                        </h3>

                        {/* SKU input only for Add */}
                        {!isEdit && (
                            <input
                                type="text"
                                placeholder="SKU"
                                value={selectedProduct?.sku || ""}
                                onChange={(e) =>
                                    setSelectedProduct({
                                        ...(selectedProduct || {}),
                                        sku: e.target.value,
                                        // Initialize other fields to satisfy TS Product type
                                        id: selectedProduct?.id || 0,
                                        name: selectedProduct?.name || "",
                                        description: selectedProduct?.description || "",
                                        price: selectedProduct?.price || 0,
                                        active: selectedProduct?.active ?? true,
                                    })
                                }
                                className="w-full border p-1 mb-2 rounded"
                            />
                        )}

                        <input
                            type="text"
                            placeholder="Name"
                            value={selectedProduct?.name || ""}
                            onChange={(e) =>
                                setSelectedProduct({ ...(selectedProduct || {}), name: e.target.value })
                            }
                            className="w-full border p-1 mb-2 rounded"
                        />

                        <input
                            type="text"
                            placeholder="Description"
                            value={selectedProduct?.description || ""}
                            onChange={(e) =>
                                setSelectedProduct({ ...(selectedProduct || {}), description: e.target.value })
                            }
                            className="w-full border p-1 mb-2 rounded"
                        />

                        <input
                            type="number"
                            placeholder="Price"
                            value={selectedProduct?.price || ""}
                            onChange={(e) =>
                                setSelectedProduct({ ...(selectedProduct || {}), price: Number(e.target.value) })
                            }
                            className="w-full border p-1 mb-2 rounded"
                        />

                        <div className="flex items-center gap-2 mb-2">
                            <input
                                type="checkbox"
                                checked={selectedProduct?.active ?? true}
                                onChange={(e) =>
                                    setSelectedProduct({ ...(selectedProduct || {}), active: e.target.checked })
                                }
                            />
                            <span>Active</span>
                        </div>

                        <div className="flex justify-end gap-2">
                            <button
                                className="px-3 py-1 bg-gray-200 text-black rounded"
                                onClick={() => {
                                    setModalOpen(false);
                                    setSelectedProduct(null);
                                }}
                            >
                                Cancel
                            </button>
                            <button
                                className="px-3 py-1 bg-gray-500 text-white rounded"
                                onClick={() => {
                                    saveProduct(selectedProduct || {});
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
