import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { pipelineService } from "@/services/pipelines";
import { jobService } from "@/services/jobs";
import type { Pipeline } from "@/types/pipeline";
import type { Job } from "@/types/job";
import { motion } from "framer-motion";
import { ArrowRight, ImageIcon, Layers, Zap } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export function DashboardPage() {
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);

  useEffect(() => {
    pipelineService.list().then(setPipelines).catch(() => {});
    jobService.list(5).then(setJobs).catch(() => {});
  }, []);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <Link to="/editor">
          <Button><Zap className="mr-2 h-4 w-4" /> New Pipeline</Button>
        </Link>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0 }}>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Saved Pipelines</CardTitle>
              <Layers className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent><div className="text-2xl font-bold">{pipelines.length}</div></CardContent>
          </Card>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Jobs</CardTitle>
              <Zap className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent><div className="text-2xl font-bold">{jobs.length}</div></CardContent>
          </Card>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Completed</CardTitle>
              <ImageIcon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent><div className="text-2xl font-bold">{jobs.filter((j) => j.status === "completed").length}</div></CardContent>
          </Card>
        </motion.div>
      </div>
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold">Recent Jobs</h2>
          <Link to="/jobs"><Button variant="ghost" size="sm">View all <ArrowRight className="ml-1 h-3 w-3" /></Button></Link>
        </div>
        <div className="space-y-2">
          {jobs.map((job) => (
            <Link key={job.id} to={`/jobs/${job.id}`}>
              <Card className="p-3 hover:bg-accent transition-colors cursor-pointer">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`h-2 w-2 rounded-full ${job.status === "completed" ? "bg-green-500" : job.status === "failed" ? "bg-red-500" : job.status === "processing" ? "bg-yellow-500" : "bg-gray-500"}`} />
                    <span className="text-sm font-mono">{job.id.slice(0, 8)}...</span>
                    <span className="text-sm text-muted-foreground">{job.total_steps} steps</span>
                  </div>
                  <span className="text-xs text-muted-foreground">{new Date(job.created_at).toLocaleDateString()}</span>
                </div>
              </Card>
            </Link>
          ))}
          {jobs.length === 0 && <p className="text-sm text-muted-foreground text-center py-8">No jobs yet. Start by creating a pipeline!</p>}
        </div>
      </div>
    </div>
  );
}
