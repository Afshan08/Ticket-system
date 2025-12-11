/**
 * Mock Data for Printy Productions
 */
const mockDB = {
    areas: [
        { id: 1, name: "Press Room", description: "Main printing area" },
        { id: 2, name: "Finishing", description: "Slitting and rewinding" },
        { id: 3, name: "Lamination", description: "Lamination station" }
    ],
    customers: [
        { id: 1, name: "Acme Corp", contact: "john@acme.com", areaId: 1 },
        { id: 2, name: "Global Prints", contact: "sarah@global.com", areaId: 1 },
        { id: 3, name: "Local Café", contact: "manager@cafe.com", areaId: 2 }
    ],
    categories: [
        { id: 1, name: "Labels", description: "Adhesive labels" },
        { id: 2, name: "Wrappers", description: "Food wrappers" },
        { id: 3, name: "Banners", description: "Large format properties" }
    ],
    items: [
        { id: 1, name: "Glossy Label 5x5", categoryId: 1, price: 0.05, specs: "5x5cm, Glossy" },
        { id: 2, name: "Burger Wrapper", categoryId: 2, price: 0.02, specs: "Greaseproof" },
        { id: 3, name: "Vinyl Banner", categoryId: 3, price: 15.00, specs: "Heavy duty vinyl" }
    ],
    machines: [
        { id: 1, name: "Heidelberg XL", areaId: 1, type: "Printer" },
        { id: 2, name: "Rotoflex VLI", areaId: 2, type: "Slitter" },
        { id: 3, name: "Comexi", areaId: 3, type: "Laminator" }
    ],
    operators: [
        { id: 1, name: "Mike Ross", role: "Printer", shift: "Day" },
        { id: 2, name: "Rachel Zane", role: "Finisher", shift: "Night" },
        { id: 3, name: "Louis Litt", role: "Manager", shift: "Day" }
    ],
    jobs: [
        { id: 101, customerId: 1, itemId: 1, qty: 5000, status: "Pending" },
        { id: 102, customerId: 2, itemId: 2, qty: 10000, status: "In Progress" }
    ]
};

// Helper to simulate API call
const getData = (table) => {
    return mockDB[table] || [];
};

const getById = (table, id) => {
    return mockDB[table].find(item => item.id == id);
};
