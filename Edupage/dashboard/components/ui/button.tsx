import { cn } from '@/lib/utils';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'solid' | 'ghost';
}

export function Button({ className, variant = 'solid', ...props }: ButtonProps) {
  const base = 'inline-flex items-center justify-center gap-2 rounded-xl text-sm font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-accent-500/40 focus:ring-offset-0';
  const variants = {
    solid: 'bg-accent-500/80 hover:bg-accent-500 text-white px-4 py-2',
    ghost: 'bg-white/5 hover:bg-white/10 text-slate-100 px-3 py-2 border border-white/10'
  };
  return <button className={cn(base, variants[variant], className)} {...props} />;
}
