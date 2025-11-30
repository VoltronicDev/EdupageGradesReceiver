import { cn } from '@/lib/utils';

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {}

export function Select({ className, children, ...props }: SelectProps) {
  return (
    <select
      className={cn(
        'bg-white/5 border border-white/10 text-sm text-slate-100 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent-500/40',
        className
      )}
      {...props}
    >
      {children}
    </select>
  );
}
