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
        { name: t.detAnal, subname: barri ? `(${barri})` : undefined, href: "/detailed" },
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
                            key={link.name + (link.subname || "")}
                            href={link.href}
                            className={`navbar-link ${isActive ? "active" : ""}`}
                        >
                            <span>
                                {link.name}
                                {link.subname && (
                                    <>
                                        <br />
                                        <span style={{ fontSize: "0.85em", fontWeight: 400, opacity: 0.9 }}>
                                            {link.subname}
                                        </span>
                                    </>
                                )}
                            </span>
                        </Link>
                    );
                })}
            </nav>

            <div className="navbar-right">
                <Dropdown
                    options={["en", "es"]}
                    optoval={{ en: "🇬🇧 English", es: "🇪🇸 Español" }}
                    value={language}
                    onChange={setLanguage}
                />
            </div>
        </header>
    );
}
