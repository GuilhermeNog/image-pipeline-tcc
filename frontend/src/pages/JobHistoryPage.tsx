import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { jobService } from "@/services/jobs";
import type { Job } from "@/types/job";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

const STATUS_COLORS: Record<string, string> = {
  completed: "bg-green-500/10 text-green-500",
  failed: "bg-red-500/10 text-red-500",
  processing: "bg-yellow-500/10 text-yellow-500",
  pending: "bg-gray-500/10 text-gray-500",
};

export function JobHistoryPage() {
  const [jobs, setJobs] = useState<Job[]>([]);

  useEffect(() => {
    jobService.list().then(setJobs).catch(() => {});
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Job History</h1>
      <div className="space-y-2">
        {jobs.map((job, i) => (
          <motion.div key={job.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
            <Link to={`/jobs/${job.id}`}>
              <Card className="p-4 hover:bg-accent transition-colors cursor-pointer">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <span className="font-mono text-sm">{job.id.slice(0, 8)}</span>
                    <Badge variant="outline" className={STATUS_COLORS[job.status]}>{job.status}</Badge>
                    <span className="text-sm text-muted-foreground">{job.current_step}/{job.total_steps} steps</span>
                  </div>
                  <span className="text-sm text-muted-foreground">{new Date(job.created_at).toLocaleString()}</span>
                </div>
              </Card>
            </Link>
          </motion.div>
        ))}
        {jobs.length === 0 && <p className="text-center text-muted-foreground py-12">No jobs yet</p>}
      </div>
    </div>
  );
}
