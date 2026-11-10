package com.infomak.moailite;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import org.json.JSONArray;
import org.json.JSONObject;
import java.net.HttpURLConnection;
import java.net.URL;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.Iterator;

/** Experimental event catalog. Never extracts or bypasses protected streams. */
public final class MoaiEventsActivity extends Activity {
    private static final String API = "https://daddylive.app/api/events";
    private static final int BG = 0xff06152d, PANEL = 0xff102b4c;
    private final Handler handler = new Handler(Looper.getMainLooper());
    private LinearLayout content;
    private TextView status;
    private boolean active = false, loading = false;
    private final Runnable reload = new Runnable() {
        @Override public void run() {
            if (active) { fetchEvents(); handler.postDelayed(this, 60000L); }
        }
    };

    private int dp(int value) { return (int)(value * getResources().getDisplayMetrics().density + .5f); }
    private GradientDrawable bg(int color) {
        GradientDrawable d = new GradientDrawable();
        d.setColor(color);
        d.setCornerRadius(dp(9));
        return d;
    }
    private TextView label(String value, int sp, boolean bold) {
        TextView t = new TextView(this);
        t.setText(value);
        t.setTextColor(Color.WHITE);
        t.setTextSize(sp);
        if (bold) t.setTypeface(null, Typeface.BOLD);
        t.setPadding(dp(12), dp(7), dp(12), dp(7));
        return t;
    }
    private Button button(String title) {
        Button b = new Button(this);
        b.setText(title);
        b.setTextColor(Color.WHITE);
        b.setTextSize(13);
        b.setAllCaps(false);
        b.setBackground(bg(0xff21466f));
        b.setPadding(dp(12), dp(4), dp(12), dp(4));
        b.setFocusable(true);
        return b;
    }
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(BG);
        root.setPadding(dp(18), dp(12), dp(18), dp(10));
        LinearLayout top = new LinearLayout(this);
        top.setOrientation(LinearLayout.HORIZONTAL);
        top.setGravity(Gravity.CENTER_VERTICAL);
        Button back = button("‹  Volver");
        back.setOnClickListener(v -> finish());
        top.addView(back);
        TextView title = label("  MOAI GAMER  ·  EVENTOS EN VIVO", 19, true);
        top.addView(title, new LinearLayout.LayoutParams(0, dp(54), 1f));
        Button refresh = button("↻ Actualizar");
        refresh.setOnClickListener(v -> fetchEvents());
        top.addView(refresh);
        root.addView(top);
        status = label("Consultando programación…", 13, false);
        status.setTextColor(0xffadcced);
        root.addView(status);
        ScrollView scroll = new ScrollView(this);
        content = new LinearLayout(this);
        content.setOrientation(LinearLayout.VERTICAL);
        scroll.addView(content);
        root.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1f));
        setContentView(root);
        back.requestFocus();
    }
    @Override protected void onResume() {
        super.onResume();
        active = true;
        handler.removeCallbacks(reload);
        reload.run();
    }
    @Override protected void onPause() {
        active = false;
        handler.removeCallbacks(reload);
        super.onPause();
    }
    private void fetchEvents() {
        if (loading) return;
        loading = true;
        status.setText("Actualizando eventos…");
        new Thread(() -> {
            String response = null, failure = null;
            HttpURLConnection connection = null;
            try {
                connection = (HttpURLConnection)new URL(API).openConnection();
                connection.setConnectTimeout(9000);
                connection.setReadTimeout(12000);
                connection.setRequestProperty("Accept", "application/json");
                connection.setRequestProperty("User-Agent", "MOAI-GAMER/0.1.83");
                int code = connection.getResponseCode();
                if (code != 200) throw new Exception("HTTP " + code);
                try (InputStream in = connection.getInputStream();
                     ByteArrayOutputStream out = new ByteArrayOutputStream()) {
                    byte[] buf = new byte[8192]; int n; int total = 0;
                    while ((n = in.read(buf)) != -1) {
                        total += n;
                        if (total > 2000000) throw new Exception("Respuesta demasiado grande");
                        out.write(buf, 0, n);
                    }
                    response = new String(out.toByteArray(), StandardCharsets.UTF_8);
                }
            } catch (Exception e) { failure = e.getMessage(); }
            finally { if (connection != null) connection.disconnect(); }
            final String json = response, error = failure;
            runOnUiThread(() -> {
                loading = false;
                if (!active || isFinishing()) return;
                if (error != null) {
                    status.setText("No se pudo actualizar: " + error + " · Reintentá más tarde");
                    return; // Keep the most recent successful list.
                }
                try { render(new JSONObject(json)); }
                catch (Exception e) { status.setText("La API devolvió datos no compatibles"); }
            });
        }, "moai-events-fetch").start();
    }
    private void render(JSONObject response) throws Exception {
        JSONObject categories = response.optJSONObject("categories");
        if (categories == null) throw new Exception("Missing categories");
        LinearLayout newContent = new LinearLayout(this);
        newContent.setOrientation(LinearLayout.VERTICAL);
        int total = 0;
        Iterator<String> keys = categories.keys();
        while (keys.hasNext() && total < 300) {
            String category = keys.next();
            JSONArray events = categories.optJSONArray(category);
            if (events == null || events.length() == 0) continue;
            TextView heading = label(category, 17, true);
            heading.setTextColor(0xff62d0ff);
            newContent.addView(heading);
            for (int i=0; i<events.length() && total<300; i++) {
                JSONObject event = events.optJSONObject(i);
                if (event == null) continue;
                total++;
                LinearLayout panel = new LinearLayout(this);
                panel.setOrientation(LinearLayout.VERTICAL);
                panel.setPadding(dp(8),dp(5),dp(8),dp(7));
                panel.setBackground(bg(PANEL));
                LinearLayout.LayoutParams margin = new LinearLayout.LayoutParams(-1,-2);
                margin.setMargins(0,0,0,dp(8));
                newContent.addView(panel,margin);
                String name = event.optString("event","Evento");
                String time = event.optString("time","");
                String source = event.optString("source","");
                panel.addView(label(name + (time.isEmpty()?"":"   ·   "+time), 15, true));
                TextView origin = label("Fuente: "+source+"  ·  enlaces externos", 11, false);
                origin.setTextColor(0xffffd766);
                panel.addView(origin);
                JSONArray links = event.optJSONArray("channels");
                if (links == null || links.length()==0) continue;
                LinearLayout buttons = new LinearLayout(this);
                buttons.setOrientation(LinearLayout.HORIZONTAL);
                panel.addView(buttons);
                for (int j=0;j<Math.min(links.length(),8);j++) {
                    JSONObject link = links.optJSONObject(j);
                    if (link == null) continue;
                    String uri = link.optString("url","");
                    Uri parsed = Uri.parse(uri);
                    if (!"https".equalsIgnoreCase(parsed.getScheme()) ||
                        !"daddylive.app".equalsIgnoreCase(parsed.getHost())) continue;
                    String caption = link.optString("channel_name","Enlace "+(j+1));
                    Button open = button(caption);
                    LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(0, dp(45), 1f);
                    p.setMargins(dp(3),0,dp(3),0);
                    buttons.addView(open,p);
                    open.setOnClickListener(v -> {
                        try { startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(uri))); }
                        catch (Exception e) { status.setText("No hay una app compatible para abrir este enlace"); }
                    });
                }
            }
        }
        content.removeAllViews();
        content.addView(newContent);
        status.setText(total+" eventos · información de terceros · actualización cada 60 s");
        if (total == 0) content.addView(label("No hay eventos disponibles en este momento.", 16, false));
    }
}