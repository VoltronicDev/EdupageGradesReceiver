'use client';

import { useEffect, useMemo, useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select } from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import { RadialProgress } from '@/components/charts/radial';
import { Sparkline } from '@/components/charts/sparkline';

interface Grade {
  id?: string;
  subject: string;
  title: string;
  percent: number;
  date?: string;
  trend?: number[];
}

interface SubjectAggregate {
  subject: string;
  average: number;
  latest?: number;
  best?: number;
  trend?: number[];
}

interface GradesResponse {
  grades: Grade[];
  subjects?: SubjectAggregate[];
  aggregates?: {
    overallAverage?: number;
    totalAssignments?: number;
    outstanding?: number;
  };
  lastUpdated?: string;
  session?: {
    status?: 'active' | 'expired' | 'pending';
    user?: string;
  };
}

const statusCopy: Record<string, { label: string; tone: string }> = {
  active: { label: 'Session active', tone: 'bg-emerald-500/30 text-emerald-100 border-emerald-400/40' },
  expired: { label: 'Session expired', tone: 'bg-rose-500/25 text-rose-100 border-rose-400/40' },
  pending: { label: 'Connecting', tone: 'bg-amber-500/25 text-amber-100 border-amber-300/40' },
};

export default function DashboardPage() {
  const [data, setData] = useState<GradesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSubject, setSelectedSubject] = useState<string>('all');
  const [minimumPercent, setMinimumPercent] = useState<number>(0);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch('/grades');
        if (!res.ok) throw new Error('Unable to fetch grades');
        const payload = (await res.json()) as GradesResponse;
        setData(payload);
      } catch (err) {
        console.error(err);
        setError('We could not load your grades right now.');
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const filteredGrades = useMemo(() => {
    if (!data?.grades) return [];
    return data.grades
      .filter((grade) => (selectedSubject === 'all' ? true : grade.subject === selectedSubject))
      .filter((grade) => grade.percent >= minimumPercent)
      .sort((a, b) => (b.date || '').localeCompare(a.date || ''));
  }, [data?.grades, minimumPercent, selectedSubject]);

  const overallAverage = useMemo(() => {
    if (data?.aggregates?.overallAverage !== undefined) return data.aggregates.overallAverage;
    if (!data?.grades?.length) return 0;
    return data.grades.reduce((sum, g) => sum + g.percent, 0) / data.grades.length;
  }, [data]);

  const lastUpdated = data?.lastUpdated ? new Date(data.lastUpdated) : new Date();

  const uniqueSubjects = useMemo(() => {
    if (data?.subjects?.length) return data.subjects.map((s) => s.subject);
    return Array.from(new Set(data?.grades?.map((g) => g.subject) ?? []));
  }, [data]);

  return (
    <main className="mx-auto max-w-6xl px-4 py-10 space-y-8">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Edupage</p>
          <h1 className="text-3xl sm:text-4xl font-bold text-gradient">Grade Dashboard</h1>
          <p className="text-slate-400 mt-2">
            Glassy overview of your latest marks, subject performance, and trends.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="outline">
            Last updated: {lastUpdated.toLocaleString()}
          </Badge>
          <Badge variant="muted">{data?.session?.user ?? 'Anonymous'}</Badge>
          <Badge variant="default" className={statusCopy[data?.session?.status ?? 'pending']?.tone}>
            {statusCopy[data?.session?.status ?? 'pending']?.label}
          </Badge>
        </div>
      </header>

      <section className="grid gap-4 md:grid-cols-3">
        <Card className="glass-highlight">
          <CardHeader>
            <div>
              <CardTitle className="text-gradient">Overall average</CardTitle>
              <CardDescription>Weighted across all recorded grades</CardDescription>
            </div>
            <RadialProgress value={overallAverage} />
          </CardHeader>
          <CardContent className="flex items-center gap-3 text-4xl font-bold">
            {overallAverage.toFixed(1)}%
            <Badge variant="muted">{filteredGrades.length} grades</Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Assignments</CardTitle>
            <Badge variant="outline">{data?.aggregates?.totalAssignments ?? filteredGrades.length} total</Badge>
          </CardHeader>
          <CardContent className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-400">Completed</p>
              <p className="text-2xl font-semibold text-slate-100">{filteredGrades.length}</p>
            </div>
            <div>
              <p className="text-sm text-slate-400">Outstanding</p>
              <p className="text-2xl font-semibold text-amber-200">
                {data?.aggregates?.outstanding ?? Math.max(0, (data?.aggregates?.totalAssignments ?? 0) - filteredGrades.length)}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Filters</CardTitle>
            <CardDescription>Refine by subject or target mark</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-sm text-slate-400">Subject</span>
              <Select value={selectedSubject} onChange={(e) => setSelectedSubject(e.target.value)} className="flex-1">
                <option value="all">All subjects</option>
                {uniqueSubjects.map((subject) => (
                  <option key={subject} value={subject}>
                    {subject}
                  </option>
                ))}
              </Select>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-slate-400">Minimum</span>
              <Select
                value={minimumPercent}
                onChange={(e) => setMinimumPercent(Number(e.target.value))}
                className="flex-1"
              >
                {[0, 50, 60, 70, 80, 90].map((value) => (
                  <option key={value} value={value}>
                    {value}%+
                  </option>
                ))}
              </Select>
              <Button variant="ghost" onClick={() => { setSelectedSubject('all'); setMinimumPercent(0); }}>
                Reset
              </Button>
            </div>
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <Card className="md:col-span-2">
          <CardHeader>
            <div>
              <CardTitle>Subjects</CardTitle>
              <CardDescription>Per-subject averages with sparklines</CardDescription>
            </div>
          </CardHeader>
          <CardContent className="grid gap-4 sm:grid-cols-2">
            {(data?.subjects ?? []).map((subject) => (
              <div key={subject.subject} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 px-4 py-3">
                <div>
                  <p className="font-semibold text-slate-100">{subject.subject}</p>
                  <p className="text-xs text-slate-400">Avg {subject.average.toFixed(1)}%</p>
                  {subject.best !== undefined && (
                    <p className="text-[11px] text-slate-500">Best {subject.best}% • Latest {subject.latest ?? subject.best}%</p>
                  )}
                </div>
                <div className="flex flex-col items-end gap-2">
                  <Badge variant="outline">{subject.average.toFixed(0)}%</Badge>
                  <Sparkline values={subject.trend ?? []} />
                </div>
              </div>
            ))}

            {!data?.subjects?.length && (
              <div className="text-slate-400 text-sm">No subject aggregates yet. Grades will populate automatically.</div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Session</CardTitle>
            <CardDescription>Connection state to Edupage</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-3">
              <div className={`h-3 w-3 rounded-full ${data?.session?.status === 'active' ? 'bg-emerald-400' : data?.session?.status === 'expired' ? 'bg-rose-400' : 'bg-amber-300'} animate-pulse`} />
              <div>
                <p className="font-semibold text-slate-100">{statusCopy[data?.session?.status ?? 'pending']?.label}</p>
                <p className="text-xs text-slate-400">{data?.session?.user ?? 'Anonymous session'}</p>
              </div>
            </div>
            <p className="text-xs text-slate-500">If your session expires, refresh or re-authenticate to continue syncing grades.</p>
          </CardContent>
        </Card>
      </section>

      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-50">Grades</h2>
            <p className="text-sm text-slate-400">Detailed breakdown with trend indicators.</p>
          </div>
          <Button variant="ghost">Export CSV</Button>
        </div>

        {loading && (
          <div className="grid gap-3 card-grid">
            {Array.from({ length: 6 }).map((_, idx) => (
              <Skeleton key={idx} className="h-32" />
            ))}
          </div>
        )}

        {error && !loading && (
          <Card className="border-rose-500/40">
            <CardHeader>
              <CardTitle className="text-rose-100">Error loading grades</CardTitle>
              <CardDescription>{error}</CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={() => location.reload()}>Retry</Button>
            </CardContent>
          </Card>
        )}

        {!loading && !error && (
          <div className="grid gap-4 card-grid">
            {filteredGrades.map((grade) => (
              <Card key={`${grade.subject}-${grade.title}-${grade.date}`} className="flex flex-col justify-between">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-400">{grade.subject}</p>
                    <CardTitle className="text-lg">{grade.title}</CardTitle>
                    <CardDescription>{grade.date ? new Date(grade.date).toLocaleDateString() : 'No date'}</CardDescription>
                  </div>
                  <Badge variant="default" className="text-lg px-3 py-1">
                    {grade.percent}%
                  </Badge>
                </div>
                <div className="mt-3 flex items-end justify-between">
                  <div className="flex items-center gap-2">
                    <div className="h-8 w-8 rounded-full bg-accent-500/30 border border-accent-500/40 flex items-center justify-center text-[11px] text-accent-100">
                      {grade.trend?.slice(-1)[0] ?? grade.percent}%
                    </div>
                    <p className="text-xs text-slate-400">Latest trend snapshot</p>
                  </div>
                  <Sparkline values={grade.trend ?? []} />
                </div>
              </Card>
            ))}

            {!filteredGrades.length && (
              <Card>
                <CardContent className="text-slate-400 text-sm">No grades match the filters yet.</CardContent>
              </Card>
            )}
          </div>
        )}
      </section>
    </main>
  );
}
