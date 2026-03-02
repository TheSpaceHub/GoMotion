"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import Dropdown from "../dropdown";
import { useDashboardContext } from "../context/DashboardContext";
import { translations } from "../translations";

export default function Navbar() {
    const pathname = usePathname();
    const { language, setLanguage, barri } = useDashboardContext();
    const t = translations[language];

    // Navigation Links
    const links = [
        { name: t.subtitle || "Overview", href: "/" },
        { name: barri ? `${t.detAnal} (${barri})` : t.detAnal, href: "/detailed" },
        { name: t.modelStatistics || "Model Statistics", href: "/model" },
    ];

    return (
        <header className="top-navbar">
            <div className="navbar-left">
                <Link href="/">
                    <img src="/GoMotionLogo.png" alt="GoMotion Logo" className="navbar-logo" />
                </Link>
            </div>

            <nav className="navbar-center">
                {links.map((link) => {
                    const isActive = pathname === link.href;
                    return (
                        <Link
                            key={link.name}
                            href={link.href}
                            className={`navbar-link ${isActive ? "active" : ""}`}
                        >
                            {link.name}
                        </Link>
                    );
                })}
            </nav>

            <div className="navbar-right">
                <Dropdown
                    options={["en", "es"]}
                    optoval={{ en: "English", es: "Español" }}
                    value={language}
                    onChange={setLanguage}
                />
            </div>
        </header>
    );
}
