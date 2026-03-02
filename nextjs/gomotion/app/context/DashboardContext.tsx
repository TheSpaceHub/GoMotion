"use client";

import React, { createContext, useContext, useState, useRef, ReactNode } from "react";
import { Fetcher } from "../page";

// Define the shape of our context
interface DashboardContextProps {
    day: string;
    setDay: (day: string) => void;
    barri: string;
    setBarri: (barri: string) => void;
    language: string;
    setLanguage: (lang: string) => void;
    fetcher: React.MutableRefObject<Fetcher | null>;
}

// Create the Context with a default undefined value
const DashboardContext = createContext<DashboardContextProps | undefined>(undefined);

// Helper function to format the initial date
const formatDate = (date: Date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
};

// Provider Component
export const DashboardProvider = ({ children }: { children: ReactNode }) => {
    const [day, setDay] = useState(formatDate(new Date()));
    const [barri, setBarri] = useState("el Raval");
    const [language, setLanguage] = useState("en");

    // Shared fetcher reference across all pages
    const fetcher = useRef<Fetcher | null>(null);
    if (fetcher.current === null) {
        // Assuming Fetcher is still exported from page or a shared location
        // We will extract Fetcher into load_data or similar, but for now it's imported from page (or we move it)
        fetcher.current = new Fetcher();
    }

    return (
        <DashboardContext.Provider value={{ day, setDay, barri, setBarri, language, setLanguage, fetcher }}>
            {children}
        </DashboardContext.Provider>
    );
};

// Custom Hook to consume the context
export const useDashboardContext = () => {
    const context = useContext(DashboardContext);
    if (!context) {
        throw new Error("useDashboardContext must be used within a DashboardProvider");
    }
    return context;
};
