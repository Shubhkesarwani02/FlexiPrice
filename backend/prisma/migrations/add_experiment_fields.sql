-- Add A/B testing experiment fields to products table
-- Migration: add_experiment_fields

-- Add experiment_group enum
CREATE TYPE "ExperimentGroup" AS ENUM ('CONTROL', 'ML_VARIANT');

-- Add experiment fields to products
ALTER TABLE "products" 
ADD COLUMN "experiment_group" "ExperimentGroup" DEFAULT 'CONTROL',
ADD COLUMN "experiment_assigned_at" TIMESTAMP(3);

-- Create experiment_metrics table
CREATE TABLE "experiment_metrics" (
    "id" SERIAL PRIMARY KEY,
    "product_id" INTEGER NOT NULL,
    "experiment_group" "ExperimentGroup" NOT NULL,
    "impressions" INTEGER NOT NULL DEFAULT 0,
    "conversions" INTEGER NOT NULL DEFAULT 0,
    "revenue" DECIMAL(12,2) NOT NULL DEFAULT 0,
    "units_sold" INTEGER NOT NULL DEFAULT 0,
    "avg_discount_pct" DECIMAL(5,2),
    "period_start" TIMESTAMP(3) NOT NULL,
    "period_end" TIMESTAMP(3) NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "experiment_metrics_product_id_fkey" 
        FOREIGN KEY ("product_id") 
        REFERENCES "products"("id") 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

-- Create indexes for experiment_metrics
CREATE UNIQUE INDEX "experiment_metrics_product_id_experiment_group_period_start_key" 
    ON "experiment_metrics"("product_id", "experiment_group", "period_start");

CREATE INDEX "experiment_metrics_experiment_group_idx" 
    ON "experiment_metrics"("experiment_group");

CREATE INDEX "experiment_metrics_period_start_period_end_idx" 
    ON "experiment_metrics"("period_start", "period_end");

-- Add comment
COMMENT ON TABLE "experiment_metrics" IS 'Tracks A/B test metrics for ML vs rule-based discount recommendations';
COMMENT ON COLUMN "products"."experiment_group" IS 'A/B test group assignment: CONTROL (rule-based) or ML_VARIANT (ML recommendations)';
