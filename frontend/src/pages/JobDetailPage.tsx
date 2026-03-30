import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { jobService } from "@/services/jobs";
import { imageService } from "@/services/images";
import type { Job } from "@/types/job";
import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

export function JobDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [job, setJob] = useState<Job | null>(null);

  useEffect(() => {
    if (id) jobService.get(id).then(setJob).catch(() => {});
  }, [id]);

  if (!job) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center gap-4">
        <Link to="/jobs"><Button variant="ghost" size="icon"><ArrowLeft className="h-4 w-4" /></Button></Link>
        <h1 className="text-2xl font-bold">Job {job.id.slice(0, 8)}</h1>
        <Badge variant="outline">{job.status}</Badge>
      </div>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-3 xl:grid-cols-4">
        {job.steps?.map((step, i) => (
          <motion.div key={step.id} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.1 }}>
            <Card className="overflow-hidden">
              <div className="aspect-square bg-muted">
                {step.result_image_path ? (
                  <img src={imageService.getStepImageUrl(job.id, step.step_number)} alt={`Step ${step.step_number}`} className="h-full w-full object-contain" />
                ) : (
                  <div className="flex h-full items-center justify-center text-muted-foreground text-sm">No result</div>
                )}
              </div>
              <div className="p-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium capitalize">{step.step_number}. {step.operation_type}</span>
                  {step.processing_time_ms !== null && <span className="text-xs text-muted-foreground">{step.processing_time_ms}ms</span>}
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
