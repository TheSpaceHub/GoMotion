"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import Dropdown from "../dropdown";
import { useDashboardContext } from "../context/DashboardContext";
import { translations } from "../translations";

export default function Sidebar() {
    const pathname = usePathname();
    const { language, setLanguage } = useDashboardContext();
    const t = translations[language];

    // Navigation Links
    const links = [
        { name: t.subtitle || "Overview", href: "/" },
        { name: t.detAnal || "Detailed Analysis", href: "/detailed" },
        { name: t.modelStatistics || "Model Statistics", href: "/model" },
        { name: t.globalStats || "Global Statistics", href: "/global" },
    ];

    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <img src="/GoMotionLogo.png" alt="GoMotion Logo" className="sidebar-logo" />
            </div>

            <nav className="sidebar-nav">
                {links.map((link) => {
                    const isActive = pathname === link.href;
                    return (
                        <Link
                            key={link.name}
                            href={link.href}
                            className={`sidebar-link ${isActive ? "active" : ""}`}
                        >
                            {link.name}
                        </Link>
                    );
                })}
            </nav>

            <div className="sidebar-footer">
                <Dropdown
                    options={["en", "es"]}
                    optoval={{ en: "English", es: "Español" }}
                    value={language}
                    onChange={setLanguage}
                />
            </div>
        </aside>
    );
}
