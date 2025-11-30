import { cn } from '@/lib/utils';

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'outline' | 'muted';
}

export function Badge({ className, variant = 'default', ...props }: BadgeProps) {
  const base = 'inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium';
  const variants = {
    default: 'bg-accent-500/30 text-accent-400 border border-accent-500/40',
    outline: 'border border-white/20 text-slate-200 bg-white/5',
    muted: 'bg-white/5 text-slate-300 border border-white/10'
  };

  return <div className={cn(base, variants[variant], className)} {...props} />;
}
