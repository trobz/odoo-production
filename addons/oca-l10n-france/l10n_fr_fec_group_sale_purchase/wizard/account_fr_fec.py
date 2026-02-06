from odoo import fields, models
from odoo.tools import SQL


class FecExportWizard(models.TransientModel):
    _inherit = "l10n_fr.fec.export.wizard"

    group_sale_purchase = fields.Boolean(
        "Group Sale and Purchase Journals", default=True
    )

    def _sql_query_fec_lines(self, query, **kwargs):
        columns = SQL(
            """
                REGEXP_REPLACE(
                    replace(
                        %(journal_alias)s.code,
                        '|',
                        '/'
                    ), '[\\t\\r\\n]', ' ', 'g'
                ) AS JournalCode,
                REGEXP_REPLACE(
                    replace(
                        %(aj_name)s,
                        '|',
                        '/'
                    ), '[\\t\\r\\n]', ' ', 'g'
                ) AS JournalLib,
                REGEXP_REPLACE(
                    replace(
                        %(move_alias)s.name,
                        '|',
                        '/'
                    ), '[\\t\\r\\n]', ' ', 'g'
                ) AS EcritureNum,
                TO_CHAR(%(move_alias)s.date, 'YYYYMMDD') AS EcritureDate,
                %(aa_code)s AS CompteNum,
                REGEXP_REPLACE(
                    replace(
                        %(aa_name)s,
                        '|',
                        '/'
                    ), '[\\t\\r\\n]', ' ', 'g'
                ) AS CompteLib,
                %(aux_fields)s,
                CASE
                    WHEN %(move_alias)s.ref IS null OR %(move_alias)s.ref = ''
                        THEN '-'
                    ELSE REGEXP_REPLACE(
                        replace(
                            %(move_alias)s.ref,
                            '|',
                            '/'
                        ), '[\\t\\r\\n]', ' ', 'g')
                    END AS PieceRef,
                TO_CHAR(COALESCE(
                    %(move_alias)s.invoice_date,
                    %(move_alias)s.date),
                    'YYYYMMDD'
                ) AS PieceDate,
                CASE
                    WHEN account_move_line.name IS NULL OR account_move_line.name = ''
                        THEN '/'
                    WHEN account_move_line.name SIMILAR TO '[\\t|\\s|\\n]*'
                        THEN '/'
                    ELSE REGEXP_REPLACE(replace(
                        account_move_line.name,
                        '|',
                        '/'), '[\\t\\n\\r]', ' ', 'g')
                    END AS EcritureLib,
                replace(
                    CASE
                        WHEN account_move_line.debit = 0
                        THEN '0,00'
                        ELSE TO_CHAR(account_move_line.debit, '000000000000000D99')
                        END, '.', ',') AS Debit,
                replace(
                    CASE
                        WHEN account_move_line.credit = 0
                        THEN '0,00'
                        ELSE TO_CHAR(account_move_line.credit, '000000000000000D99')
                        END, '.', ',') AS Credit,
                CASE
                    WHEN %(full_alias)s.id IS NULL
                    THEN ''::text
                    ELSE %(full_alias)s.id::text
                    END AS EcritureLet,
                CASE
                    WHEN account_move_line.full_reconcile_id IS NULL
                    THEN ''
                    ELSE TO_CHAR(%(full_alias)s.create_date, 'YYYYMMDD')
                    END AS DateLet,
                TO_CHAR(%(move_alias)s.date, 'YYYYMMDD') AS ValidDate,
                CASE
                    WHEN
                        account_move_line.amount_currency IS NULL OR
                        account_move_line.amount_currency = 0
                    THEN ''
                    ELSE replace(
                        TO_CHAR(
                            account_move_line.amount_currency,
                            '000000000000000D99'
                        ),
                        '.',
                        ','
                    ) END AS Montantdevise,
                CASE
                    WHEN account_move_line.currency_id IS NULL
                    THEN ''
                    ELSE %(currency_alias)s.name
                    END AS Idevise
            """,
            currency_alias=SQL.identifier(
                query.left_join(
                    "account_move_line",
                    "currency_id",
                    "res_currency",
                    "id",
                    "currency_id",
                )
            ),
            full_alias=SQL.identifier(
                query.left_join(
                    "account_move_line",
                    "full_reconcile_id",
                    "account_full_reconcile",
                    "id",
                    "full_reconcile_id",
                )
            ),
            journal_alias=SQL.identifier(
                query.left_join(
                    "account_move_line",
                    "journal_id",
                    "account_journal",
                    "id",
                    "journal_id",
                )
            ),
            move_alias=SQL.identifier(
                query.left_join(
                    "account_move_line", "move_id", "account_move", "id", "move_id"
                )
            ),
            partner_alias=SQL.identifier(
                query.left_join(
                    "account_move_line", "partner_id", "res_partner", "id", "partner_id"
                )
            ),
            account_alias=SQL.identifier(kwargs.get("account_alias")),
            aj_name=kwargs.get("aj_name"),
            aa_code=kwargs.get("aa_code"),
            aa_name=kwargs.get("aa_name"),
            aux_fields=self._get_aux_fields(),
        )
        return columns

    def _sql_query_fec_lines2(self, query, **kwargs):
        columns = SQL(
            """
                REGEXP_REPLACE(
                    replace(
                        STRING_AGG(DISTINCT %(journal_alias)s.code, ';'),
                        '|',
                        '/'
                    ), '[\\t\\r\\n]', ' ', 'g'
                ) AS JournalCode,
                REGEXP_REPLACE(
                    replace(
                        STRING_AGG(DISTINCT %(aj_name)s, ';'),
                        '|',
                        '/'
                    ), '[\\t\\r\\n]', ' ', 'g'
                ) AS JournalLib,
                REGEXP_REPLACE(
                    replace(
                        %(move_alias)s.name,
                        '|',
                        '/'
                    ), '[\\t\\r\\n]', ' ', 'g'
                ) AS EcritureNum,
                TO_CHAR(MAX(%(move_alias)s.date), 'YYYYMMDD') AS EcritureDate,
                STRING_AGG(DISTINCT %(aa_code)s, ';') AS CompteNum,
                REGEXP_REPLACE(
                    replace(
                        STRING_AGG(DISTINCT %(aa_name)s, ';'),
                        '|',
                        '/'
                    ), '[\\t\\r\\n]', ' ', 'g'
                ) AS CompteLib,
                %(aux_fields)s,
                CASE
                    WHEN MIN(%(move_alias)s.ref) IS null OR MIN(%(move_alias)s.ref) = ''
                        THEN '-'
                    ELSE REGEXP_REPLACE(
                        replace(
                            MIN(%(move_alias)s.ref),
                            '|',
                            '/'
                        ), '[\\t\\r\\n]', ' ', 'g')
                    END AS PieceRef,
                TO_CHAR(MAX(COALESCE(
                    %(move_alias)s.invoice_date,
                    %(move_alias)s.date)),
                    'YYYYMMDD'
                ) AS PieceDate,
                CASE
                    WHEN MIN(account_move_line.name) IS NULL
                        OR MIN(account_move_line.name) = ''
                        THEN '/'
                    WHEN MIN(account_move_line.name) SIMILAR TO '[\\t|\\s|\\n]*'
                        THEN '/'
                    ELSE REGEXP_REPLACE(replace(
                        MIN(account_move_line.name),
                        '|',
                        '/'), '[\\t\\n\\r]', ' ', 'g')
                    END AS EcritureLib,
                replace(
                    CASE
                        WHEN SUM(account_move_line.debit) = 0
                        THEN '0,00'
                        ELSE TO_CHAR(
                            SUM(account_move_line.debit),
                            '000000000000000D99'
                        )
                        END, '.', ',') AS Debit,
                replace(
                    CASE
                        WHEN SUM(account_move_line.credit) = 0
                        THEN '0,00'
                        ELSE TO_CHAR(
                            SUM(account_move_line.credit),
                            '000000000000000D99'
                        )
                        END, '.', ',') AS Credit,
                CASE
                    WHEN MIN(%(full_alias)s.id) IS NULL
                    THEN ''::text
                    ELSE MIN(%(full_alias)s.id)::text
                    END AS EcritureLet,
                CASE
                    WHEN MIN(account_move_line.full_reconcile_id) IS NULL
                    THEN ''
                    ELSE TO_CHAR(MIN(%(full_alias)s.create_date), 'YYYYMMDD')
                    END AS DateLet,
                TO_CHAR(MIN(%(move_alias)s.date), 'YYYYMMDD') AS ValidDate,
                CASE
                    WHEN
                        MIN(account_move_line.amount_currency) IS NULL OR
                        MIN(account_move_line.amount_currency) = 0
                    THEN ''
                    ELSE replace(
                        TO_CHAR(
                            MIN(account_move_line.amount_currency),
                            '000000000000000D99'
                        ),
                        '.',
                        ','
                    ) END AS Montantdevise,
                CASE
                    WHEN MIN(account_move_line.currency_id) IS NULL
                    THEN ''
                    ELSE MIN(%(currency_alias)s.name)
                    END AS Idevise
            """,
            currency_alias=SQL.identifier(
                query.left_join(
                    "account_move_line",
                    "currency_id",
                    "res_currency",
                    "id",
                    "currency_id",
                )
            ),
            full_alias=SQL.identifier(
                query.left_join(
                    "account_move_line",
                    "full_reconcile_id",
                    "account_full_reconcile",
                    "id",
                    "full_reconcile_id",
                )
            ),
            journal_alias=SQL.identifier(
                query.left_join(
                    "account_move_line",
                    "journal_id",
                    "account_journal",
                    "id",
                    "journal_id",
                )
            ),
            move_alias=SQL.identifier(
                query.left_join(
                    "account_move_line", "move_id", "account_move", "id", "move_id"
                )
            ),
            partner_alias=SQL.identifier(
                query.left_join(
                    "account_move_line", "partner_id", "res_partner", "id", "partner_id"
                )
            ),
            account_alias=SQL.identifier(kwargs.get("account_alias")),
            aj_name=kwargs.get("aj_name"),
            aa_code=kwargs.get("aa_code"),
            aa_name=kwargs.get("aa_name"),
            aux_fields=self._get_aux_fields(),
        )
        return columns

    def _get_rows_fec_lines(self):
        if not self.group_sale_purchase:
            return super()._get_rows_fec_lines()

        query_limit = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("l10n_fr_fec.batch_size", 500000)
        )
        query = self.env["account.move.line"]._search(
            domain=self._get_base_domain()
            + [
                ("date", ">=", self.date_from),
                ("date", "<=", self.date_to),
                ("journal_id.type", "not in", ["sale", "purchase"]),
            ],
            limit=query_limit + 1,
            order="date, move_name, id",
        )
        account_alias = query.join(
            "account_move_line", "account_id", "account_account", "id", "account_id"
        )
        params = {
            "account_alias": account_alias,
            "aa_name": self.env["account.account"]._field_to_sql(
                account_alias,
                "name",
            ),
            "aa_code": self.env["account.account"]._field_to_sql(
                account_alias, "code", query
            ),
            "aj_name": self.env["account.journal"]._field_to_sql(
                "account_move_line__journal_id", "name"
            ),
        }
        columns = self._sql_query_fec_lines(query, **params)

        query2 = self.env["account.move.line"]._search(
            domain=self._get_base_domain()
            + [
                ("date", ">=", self.date_from),
                ("date", "<=", self.date_to),
                ("journal_id.type", "in", ["sale", "purchase"]),
            ],
            limit=query_limit + 1,
            order="date,move_name,id",
        )
        account_alias2 = query2.join(
            "account_move_line", "account_id", "account_account", "id", "account_id"
        )
        params2 = {
            "account_alias": account_alias2,
            "aa_name": self.env["account.account"]._field_to_sql(
                account_alias2,
                "name",
            ),
            "aa_code": self.env["account.account"]._field_to_sql(
                account_alias2, "code", query2
            ),
            "aj_name": self.env["account.journal"]._field_to_sql(
                "account_move_line__journal_id", "name"
            ),
        }
        columns2 = self._sql_query_fec_lines2(query2, **params2)
        query2.groupby = SQL("""
            account_move_line__move_id.name,
            account_move_line__account_id.id,
            account_move_line__partner_id.id
        """)
        query2.order = SQL("""
            MIN(account_move_line.date),
            MIN(account_move_line.move_name),
            MIN(account_move_line.id)
        """)

        sql_query = SQL(
            """
                (%s)
                UNION
                (%s)
                ORDER BY PieceDate, EcritureNum
            """,
            query.select(columns),
            query2.select(columns2),
        )
        rows_to_write = []
        self._cr.execute(sql_query)
        query_results = self._cr.fetchall()
        rows_to_write.append(query_results[:query_limit])
        return rows_to_write
