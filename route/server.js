require("dotenv").config();
const express = require("express");
const { Client } = require("@notionhq/client");

const app = express();
const port = process.env.PORT || 3000;
const notion = new Client({ auth: process.env.NOTION_API_KEY });
const DATABASE_ID = process.env.NOTION_DATABASE_ID;

app.use(express.static("public")); // フロントエンド用の静的ファイルを提供

app.get("/config", (req, res) => {
    res.json({ googleMapsApiKey: process.env.GOOGLE_MAPS_API_KEY });
});

app.get("/get-routes", async (req, res) => {
    const assignedTo = req.query.assignedTo;
    if (!assignedTo) return res.status(400).json({ error: "担当者を指定してください" });

    try {
        console.log(`📌 担当者: ${assignedTo}`);
        const response = await notion.databases.query({
            database_id: DATABASE_ID,
            filter: {
                and: [
                    { property: "担当者", select: { equals: assignedTo } },
                    { property: "配送完了", checkbox: { equals: false } }
                ]
            }
        });

        // **レスポンスをログに出力**
        console.log("📌 [DEBUG] Notion API レスポンス:", JSON.stringify(response, null, 2));

        // **レスポンスの構造を確認**
        if (!response.results) {
            console.error("❌ Notion API からデータを取得できませんでした");
            return res.status(500).json({ error: "Notion API データ取得エラー" });
        }

        const addresses = response.results
            .map(page => {
                const address = page.properties?.住所?.rich_text?.[0]?.text?.content;
                if (!address) {
                    console.warn("⚠️ [警告] 住所データが見つからないページ:", page.id);
                    return null;
                }
                return address;
            })
            .filter(address => address !== null); // `null` のデータを除外

        console.log(`📌 [DEBUG] 取得した住所リスト (${addresses.length} 件):`, addresses);

        if (addresses.length === 0) {
            console.warn("⚠️ [警告] 配送未完了の住所データが取得できませんでした");
        }

        res.json(addresses);
    } catch (error) {
        console.error("❌ Notion API のエラー:", error);
        res.status(500).json({ error: `Notion API のエラー: ${error.message}` });
    }
});

app.listen(port, () => console.log(`🚀 Server running at http://localhost:${port}`));
