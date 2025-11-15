-- Migration to add expires_at field to batch_discounts table
-- This is a SQL migration that corresponds to the Prisma schema changes

-- Add expires_at column
ALTER TABLE batch_discounts 
ADD COLUMN expires_at TIMESTAMP;

-- Add indexes for performance
CREATE INDEX idx_batch_discounts_batch_valid 
ON batch_discounts(batch_id, valid_from, valid_to);

CREATE INDEX idx_batch_discounts_expires 
ON batch_discounts(expires_at);

-- Update existing records to set expires_at based on batch expiry
UPDATE batch_discounts bd
SET expires_at = ib.expiry_date
FROM inventory_batches ib
WHERE bd.batch_id = ib.id
  AND bd.expires_at IS NULL;

-- Add comment
COMMENT ON COLUMN batch_discounts.expires_at IS 'When this discount expires (typically same as batch expiry_date)';
