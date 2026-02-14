'use client';

import { motion } from 'framer-motion';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs) {
    return twMerge(clsx(inputs));
}

export const FadeIn = ({ children, delay = 0, className }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay }}
        className={className}
    >
        {children}
    </motion.div>
);

export const GlassCard = ({ children, className, hoverEffect = true }) => (
    <motion.div
        className={cn(
            "glass-card relative overflow-hidden group",
            hoverEffect && "hover:-translate-y-1",
            className
        )}
        whileHover={hoverEffect ? { scale: 1.02 } : {}}
    >
        {/* Shine effect */}
        {hoverEffect && (
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:animate-shine pointer-events-none" />
        )}
        {children}
    </motion.div>
);
