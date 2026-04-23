-- ============================================================
-- SEED DATA for Multi-Agent Customer Support System
-- Run this in: Supabase Dashboard → SQL Editor → Run
-- ============================================================

-- =====================
-- TABLE: customers (12 rows)
-- =====================
INSERT INTO customers (name, email, tier) VALUES
('Alice Johnson',  'alice.johnson@email.com', 'premium'),
('Bob Martinez',   'bob.martinez@email.com',  'standard'),
('Carol Singh',    'carol.singh@email.com',   'premium'),
('David Kim',      'david.kim@email.com',     'standard'),
('Emma Thompson',  'emma.t@email.com',        'premium'),
('Frank Nguyen',   'frank.nguyen@email.com',  'standard'),
('Grace Patel',    'grace.patel@email.com',   'standard'),
('Henry Wilson',   'henry.w@email.com',       'premium'),
('Isla Brown',     'isla.brown@email.com',    'standard'),
('James Lee',      'james.lee@email.com',     'standard'),
('Karen White',    'karen.white@email.com',   'premium'),
('Leo Fernandez',  'leo.f@email.com',         'standard');


-- =====================
-- TABLE: orders (12 rows)
-- =====================
INSERT INTO orders (customer_id, product, amount, status, order_date) VALUES
(1,  'Wireless Headphones',   89.99,  'delivered',  '2026-03-15'),
(2,  'Laptop Stand',          45.00,  'delivered',  '2026-03-20'),
(3,  'Mechanical Keyboard',  129.99,  'delivered',  '2026-03-22'),
(4,  'USB-C Hub',             35.50,  'processing', '2026-04-10'),
(5,  'Monitor 27"',          349.00,  'delivered',  '2026-03-01'),
(6,  'Webcam HD',             79.99,  'cancelled',  '2026-03-28'),
(7,  'Mouse Pad XL',          19.99,  'delivered',  '2026-04-05'),
(8,  'Ergonomic Chair',      399.00,  'delivered',  '2026-02-14'),
(9,  'Phone Stand',           12.99,  'processing', '2026-04-18'),
(10, 'Blue Light Glasses',    29.99,  'delivered',  '2026-04-01'),
(11, 'Desk Lamp LED',         54.99,  'delivered',  '2026-03-10'),
(12, 'Cable Management Kit',  22.50,  'cancelled',  '2026-04-12');


-- =====================
-- TABLE: support_tickets (12 rows)
-- =====================
INSERT INTO support_tickets (customer_id, issue, status) VALUES
(1,  'Headphones stopped working after 2 weeks',            'open'),
(2,  'Wrong item delivered — received a mouse instead',     'escalated'),
(3,  'Keyboard keys are sticky out of the box',            'open'),
(4,  'Order stuck in processing for 10 days',              'open'),
(5,  'Monitor has dead pixels, need replacement',          'escalated'),
(6,  'Cancelled order but still got charged',              'resolved'),
(7,  'Package delivered to wrong address',                 'escalated'),
(8,  'Chair arrived with a broken armrest',                'resolved'),
(9,  'No shipping confirmation email received',            'open'),
(10, 'Item not as described on the website',               'open'),
(11, 'Desk lamp flickers intermittently',                  'resolved'),
(12, 'Refund not processed after 2 weeks of cancellation', 'escalated');
