CREATE INDEX idx_pos_order_line_order_id ON pos_order_line (order_id); -- already exists
CREATE INDEX idx_pos_order_session_id ON pos_order (session_id); -- already exists
CREATE INDEX idx_pos_order_company_id ON pos_order (company_id); -- already exists
CREATE INDEX idx_pos_session_config_id ON pos_session (config_id); -- already exists
CREATE INDEX idx_pos_config_company_team ON pos_config (company_id, crm_team_id);


-- load pos order
CREATE INDEX idx_pos_order_line_sale_order_origin_id
ON pos_order_line (sale_order_origin_id);
CREATE INDEX idx_pos_order_line_refunded_orderline_id
ON pos_order_line (refunded_orderline_id);

-- load sale order
CREATE INDEX idx_purchase_order_line_group_id
ON purchase_order_line (group_id);

-- confirm sale order:
CREATE INDEX idx_pos_order_line_sale_order_line_id
ON pos_order_line (sale_order_line_id);


-- load pos session:
CREATE INDEX idx_stock_move_line_product_id
ON stock_move_line (product_id);

CREATE INDEX idx_product_template_pos_filter
ON product_template (company_id, available_in_pos, sale_ok);

CREATE INDEX idx_product_product_active_tmpl
ON product_product (active, product_tmpl_id);