"use client";

import {Inter} from 'next/font/google';
import './globals.css';
import React from 'react';
import Navbar from '@/components/navbar';
import {AnimatePresence} from 'framer-motion';
import PageTransition from '@/components/page-transition';

const inter = Inter({subsets: ['latin']});

export default function RootLayout({
                                       children,
                                   }: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
        <body className={inter.className}>
        <Navbar/>
        <AnimatePresence mode="wait">
            <PageTransition key={typeof window !== 'undefined' ? window.location.pathname : ''}>
                {children}
            </PageTransition>
        </AnimatePresence>
        </body>
        </html>
    );
}
