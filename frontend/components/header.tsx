import React from "react";
import Image from "next/image";
import Logo from "@/assets/GW Open Source Program Office.png";
import { ThemeToggle } from "@/components/theme-toggle";

/*
Header Component
- Displays the application header with logo
- Includes ThemeToggle for switching between Light/Dark modes
*/

const Header = () => {
  return (
    <header className="p-6">
      <div className="flex items-center justify-between">
        <Image
          src={Logo}
          alt="Logo"
          width={60}
          height={60}
          className="rounded-lg"
        />
        <ThemeToggle />
      </div>
    </header>
  );
};

export default Header;
