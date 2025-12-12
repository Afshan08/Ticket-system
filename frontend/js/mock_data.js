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
        { id: 3, name: "Local Café", contact: "manager@cafe.com", areaId: 2 },
        { id: 4, name: "RetailCo", contact: "buyer@retailco.com", areaId: 1 },
        { id: 5, name: "TechWrap Inc", contact: "ops@techwrap.com", areaId: 2 }
    ],
    categories: [
        { id: 1, name: "Labels", description: "Adhesive labels" },
        { id: 2, name: "Wrappers", description: "Food wrappers" },
        { id: 3, name: "Banners", description: "Large format properties" },
        { id: 4, name: "Sleeves", description: "Shrink sleeves" }
    ],
    items: [
        { id: 1, name: "Glossy Label 5x5", categoryId: 1, price: 0.05, specs: "5x5cm, Glossy" },
        { id: 2, name: "Burger Wrapper", categoryId: 2, price: 0.02, specs: "Greaseproof" },
        { id: 3, name: "Vinyl Banner", categoryId: 3, price: 15.00, specs: "Heavy duty vinyl" },
        { id: 4, name: "Snack Pouch", categoryId: 2, price: 0.15, specs: "Multilayer" },
        { id: 5, name: "Water Bottle Label", categoryId: 1, price: 0.03, specs: "BOPP Clear" },
        { id: 6, name: "Shrink Sleeve", categoryId: 4, price: 0.12, specs: "PVC Shrink" }
    ],
    machines: [
        { id: 1, name: "Heidelberg XL", areaId: 1, type: "Printer" },
        { id: 2, name: "Rotoflex VLI", areaId: 2, type: "Slitter" },
        { id: 3, name: "Comexi", areaId: 3, type: "Laminator" },
        { id: 4, name: "Flexo 2", areaId: 1, type: "Printer" },
        { id: 5, name: "Titan Slitter", areaId: 2, type: "Slitter" }
    ],
    operators: [
        { id: 1, name: "Mike Ross", role: "Printer", shift: "Day" },
        { id: 2, name: "Rachel Zane", role: "Finisher", shift: "Night" },
        { id: 3, name: "Louis Litt", role: "Manager", shift: "Day" },
        { id: 4, name: "John Doe", role: "Printer", shift: "Night" },
        { id: 5, name: "Jane Smith", role: "Finisher", shift: "Day" }
    ],
    jobs: [
        { id: 101, customerId: 1, itemId: 1, qty: 50000, status: "Pending", orderDate: "2025-11-20", dueDate: "2025-12-05", priority: "High" },
        { id: 102, customerId: 2, itemId: 2, qty: 100000, status: "In Progress", orderDate: "2025-11-25", dueDate: "2025-12-15", priority: "Medium" },
        { id: 103, customerId: 3, itemId: 5, qty: 25000, status: "Completed", orderDate: "2025-11-15", dueDate: "2025-11-30", priority: "Low" },
        { id: 104, customerId: 4, itemId: 4, qty: 120000, status: "In Progress", orderDate: "2025-12-01", dueDate: "2025-12-20", priority: "High" },
        { id: 105, customerId: 5, itemId: 6, qty: 15000, status: "Pending", orderDate: "2025-12-05", dueDate: "2025-12-12", priority: "High" },
        { id: 106, customerId: 1, itemId: 5, qty: 80000, status: "Completed", orderDate: "2025-11-10", dueDate: "2025-11-25", priority: "Medium" }
    ],
    // Transactions: linked to Jobs
    // Type: Printing, Rewinding, Laminating, Slitting
    transactions: [
        // Job 102 (In Progress - Printing Done)
        { id: 1, jobId: 102, type: "Printing", date: "2025-11-28", machineId: 4, operatorId: 1, inputWeight: 2500, outputWeight: 2400, waste: 100, startTime: "08:00", endTime: "16:00" },
        { id: 2, jobId: 102, type: "Printing", date: "2025-11-29", machineId: 4, operatorId: 4, inputWeight: 2500, outputWeight: 2450, waste: 50, startTime: "08:00", endTime: "16:00" },

        // Job 103 (Completed)
        { id: 3, jobId: 103, type: "Printing", date: "2025-11-16", machineId: 1, operatorId: 1, inputWeight: 800, outputWeight: 750, waste: 50, startTime: "09:00", endTime: "14:00" },
        { id: 4, jobId: 103, type: "Laminating", date: "2025-11-17", machineId: 3, operatorId: 5, inputWeight: 750, outputWeight: 740, waste: 10, startTime: "10:00", endTime: "12:00" },
        { id: 5, jobId: 103, type: "Slitting", date: "2025-11-18", machineId: 2, operatorId: 2, inputWeight: 740, outputWeight: 720, waste: 20, slitWidth: "85mm", producedQty: 25100, startTime: "13:00", endTime: "17:00" },

        // Job 104 (In Progress - Printing Started)
        { id: 6, jobId: 104, type: "Printing", date: "2025-12-05", machineId: 4, operatorId: 1, inputWeight: 3000, outputWeight: 2900, waste: 100, startTime: "07:00", endTime: "19:00" },

        // Job 106 (Completed)
        { id: 7, jobId: 106, type: "Printing", date: "2025-11-12", machineId: 1, operatorId: 1, inputWeight: 2000, outputWeight: 1950, waste: 50, startTime: "08:00", endTime: "16:00" },
        { id: 8, jobId: 106, type: "Rewinding", date: "2025-11-13", machineId: 2, operatorId: 2, inputWeight: 1950, outputWeight: 1940, waste: 10, startTime: "08:00", endTime: "10:00" },
        { id: 9, jobId: 106, type: "Slitting", date: "2025-11-15", machineId: 2, operatorId: 5, inputWeight: 1940, outputWeight: 1900, waste: 40, slitWidth: "125mm", producedQty: 80500, startTime: "10:00", endTime: "18:00" }
    ]
};

// Helper to simulate API call
const getData = (table) => {
    return mockDB[table] || [];
};

const getById = (table, id) => {
    return mockDB[table].find(item => item.id == id);
};

// Report Helpers
const getJobsWithDetails = () => {
    return mockDB.jobs.map(job => {
        const customer = getById('customers', job.customerId);
        const item = getById('items', job.itemId);
        return { ...job, customerName: customer ? customer.name : 'Unknown', itemName: item ? item.name : 'Unknown' };
    });
};

const getTransactionsWithDetails = (typeFilter = null) => {
    let trans = mockDB.transactions;
    if (typeFilter) {
        trans = trans.filter(t => t.type === typeFilter);
    }
    return trans.map(t => {
        const job = getById('jobs', t.jobId);
        const machine = getById('machines', t.machineId);
        const operator = getById('operators', t.operatorId);
        return {
            ...t,
            jobNo: job ? `JOB-${job.id}` : 'JOB-?',
            machineName: machine ? machine.name : 'Unknown',
            operatorName: operator ? operator.name : 'Unknown'
        };
    });
};
