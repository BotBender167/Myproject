import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
    'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors duration-200 border',
    {
        variants: {
            variant: {
                default:
                    'bg-brand-600/20 text-brand-300 border-brand-500/30',
                secondary:
                    'bg-slate-800 text-slate-300 border-slate-700',
                success:
                    'bg-emerald-600/20 text-emerald-300 border-emerald-500/30',
                warning:
                    'bg-amber-600/20 text-amber-300 border-amber-500/30',
                destructive:
                    'bg-red-600/20 text-red-300 border-red-500/30',
                low:
                    'bg-emerald-600/20 text-emerald-300 border-emerald-500/30',
                medium:
                    'bg-amber-600/20 text-amber-300 border-amber-500/30',
                high:
                    'bg-red-600/20 text-red-300 border-red-500/30',
            },
        },
        defaultVariants: { variant: 'default' },
    },
)

export interface BadgeProps
    extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> { }

export function Badge({ className, variant, ...props }: BadgeProps) {
    return (
        <div className={cn(badgeVariants({ variant }), className)} {...props} />
    )
}
