// components/PageTransition.tsx
"use client";

import {motion} from 'framer-motion';
import {usePathname} from 'next/navigation';
import React, {useEffect, useState} from 'react';

const variants = {
    hidden: {y: 20, opacity: 0},
    enter: {y: 0, opacity: 1},
    exit: {opacity: 0},
};

const PageTransition: React.FC<{ children: React.ReactNode }> = ({children}) => {
    const pathname = usePathname();
    const [displayedPath, setDisplayedPath] = useState(pathname);

    useEffect(() => {
        setDisplayedPath(pathname);
    }, [pathname]);

    return (
        <motion.div
            key={displayedPath}
            initial="hidden"
            animate="enter"
            exit="exit"
            variants={variants}
            transition={{type: 'easeInOut', duration: 0.75}}
        >
            {children}
        </motion.div>
    );
};

export default PageTransition;
