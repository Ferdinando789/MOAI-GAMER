package com.infomak.moailite;

import android.app.Activity;
import android.app.AlertDialog;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import org.json.JSONObject;
import java.net.HttpURLConnection;
import java.net.URL;
import java.io.InputStream;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * TV extension manager: inspect trusted manifests and update sources through
 * MOAI's existing SourceManager (the host validates plugin packages).
 * Arbitrary executable URL installation is intentionally not supported.
 */
public final class MoaiExtensionsActivity extends MoaiSettingsActivity {
    private static final String DADDY_MANIFEST =
        "https://raw.githubusercontent.com/dariomadeira/moaiplug_daddylive/main/manifest.json";
    private final ExecutorService worker = Executors.newSingleThreadExecutor();
    private final Handler ui = new Handler(Looper.getMainLooper());
    private LinearLayout root;
    private TextView status;
    private boolean busy;
    private SourceManager manager() {
        return ((MoaiLiteApp)getApplication()).getPluginManager();
    }
    private int dp(int n) { return (int)(getResources().getDisplayMetrics().density*n+.5f); }
    private GradientDrawable background(int color) {
        GradientDrawable g=new GradientDrawable();
        g.setColor(color);
        g.setCornerRadius(dp(12));
        return g;
    }
    private TextView text(String label,int size,int color) {
        TextView t=new TextView(this);
        t.setText(label);
        t.setTextSize(size);
        t.setTextColor(color);
        t.setPadding(dp(12),dp(7),dp(12),dp(7));
        return t;
    }
    private void button(LinearLayout into,String title,Runnable action) {
        Button b=new Button(this);
        b.setText(title);
        b.setAllCaps(false);
        b.setTextColor(Color.WHITE);
        b.setTextSize(14);
        MoaiSettingsStyle.control(b);
        b.setFocusable(true);
        LinearLayout.LayoutParams params=new LinearLayout.LayoutParams(-1,dp(48));
        params.topMargin=dp(6);
        params.bottomMargin=dp(3);
        into.addView(b,params);
        if("Consultar versión y catálogo".equals(title))b.setTag("extension-first-action");
        b.setOnClickListener(v -> {
            if(busy){status.setText("Hay una actualización en curso");return;}
            action.run();
        });
    }
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        ScrollView scroll=new ScrollView(this);
        scroll.setBackgroundColor(0xff06152d);
        root=new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(22),dp(14),dp(22),dp(18));
        scroll.addView(root);
        root.addView(text("EXTENSIONES DE CANALES",19,MoaiSettingsStyle.WHITE));
        root.addView(text("Administrá los plugins compatibles con MOAI GAMER. Las copias de seguridad siguen disponibles en Canales, extensiones y copias.",13,0xffb8cce5));
        status=text("Los canales existentes no se eliminan al desactivar una fuente.",12,0xff8bd7f2);
        root.addView(status);
        source("moai_daddylive","Moai DaddyLive",DADDY_MANIFEST);
        source("moai_ar","Moai Argentina",null);
        button(root,"Volver a Canales, extensiones y copias",this::finish);
        setContentView(scroll);
        // Set the initial D-pad target only after every control has been styled.
        root.post(() -> {
            View first = root.findViewWithTag("extension-first-action");
            if(first!=null)first.requestFocus();
        });
    }
    private void source(String id,String title,String manifestUrl) {
        LinearLayout card=new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setPadding(dp(10),dp(10),dp(10),dp(12));
        card.setBackground(MoaiSettingsStyle.shape(this,0xff10263e,0xff294462,12));
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);
        lp.setMargins(0,dp(9),0,dp(9));
        root.addView(card,lp);
        TextView heading=text(title,17,MoaiSettingsStyle.WHITE);
        heading.setTypeface(null,android.graphics.Typeface.BOLD);
        card.addView(heading);
        TextView info=text("Fuente: "+id+" · "+(AppOptions.enabled(this,id)?"Activada":"Desactivada"),12,0xffc0ddff);
        card.addView(info);
        if(manifestUrl!=null) {
            TextView version=text("Versión disponible: consultar GitHub",12,0xfff6d776);
            card.addView(version);
            button(card,"Consultar versión y catálogo",()->queryManifest(manifestUrl,id,version));
        }
        button(card,"Actualizar "+title,()->{
            new AlertDialog.Builder(this)
                .setTitle("Actualizar "+title)
                .setMessage("MOAI consultará su fuente configurada. El gestor original debe validar la extensión antes de cargarla. ¿Continuar?")
                .setNegativeButton("Cancelar",null)
                .setPositiveButton("Actualizar",(d,w)->update(id,title,info))
                .show();
        });
        final Button toggle = new Button(this);
        toggle.setText(AppOptions.enabled(this,id)?"Desactivar fuente":"Activar fuente");
        MoaiSettingsStyle.control(toggle);
        LinearLayout.LayoutParams toggleParams=new LinearLayout.LayoutParams(-1,dp(48));
        toggleParams.topMargin=dp(7);card.addView(toggle,toggleParams);
        toggle.setOnClickListener(v->{
            if(busy)return;
            boolean next=!AppOptions.enabled(this,id);
            AppOptions.prefs(this).edit().putBoolean(id,next).apply();
            info.setText("Fuente: "+id+" · "+(next?"Activada":"Desactivada"));
            toggle.setText(next?"Desactivar fuente":"Activar fuente");
            status.setText(title+": "+(next?"activada":"desactivada")+". Volvé a Canales para aplicar los cambios.");
        });
    }
    private void update(String id,String title,TextView info) {
        busy=true;
        status.setText("Actualizando "+title+"…");
        worker.submit(()->{
            String message;
            try {
                manager().refresh(id);
                message=title+" actualizada. Reiniciá el catálogo de canales para comprobarla.";
            } catch(Exception e) {
                message="No se pudo actualizar "+title+": "+e.getClass().getSimpleName();
            }
            final String result=message;
            ui.post(()->{
                if(isFinishing()||isDestroyed())return;
                busy=false;
                status.setText(result);
                info.setText("Fuente: "+id+" · "+(AppOptions.enabled(this,id)?"Activada":"Desactivada"));
            });
        });
    }
    private void queryManifest(String location,String expectedId,TextView result) {
        busy=true;
        status.setText("Consultando el manifiesto oficial…");
        worker.submit(()->{
            HttpURLConnection c=null;
            String description;
            try {
                URL url=new URL(location);
                if(!"https".equalsIgnoreCase(url.getProtocol())||
                   !"raw.githubusercontent.com".equalsIgnoreCase(url.getHost()))
                    throw new IllegalStateException("Origen no autorizado");
                c=(HttpURLConnection)url.openConnection();
                c.setConnectTimeout(10000);
                c.setReadTimeout(15000);
                c.setInstanceFollowRedirects(false);
                if(c.getResponseCode()!=200)throw new IllegalStateException("HTTP "+c.getResponseCode());
                byte[] bytes;
                try(InputStream in=c.getInputStream();ByteArrayOutputStream out=new ByteArrayOutputStream()){
                    byte[] buffer=new byte[4096];int n;
                    while((n=in.read(buffer))!=-1){
                        if(out.size()+n>1024*1024)throw new IllegalStateException("Manifiesto demasiado grande");
                        out.write(buffer,0,n);
                    }
                    bytes=out.toByteArray();
                }
                JSONObject meta=new JSONObject(new String(bytes,StandardCharsets.UTF_8));
                if(!expectedId.equals(meta.optString("id")))throw new IllegalStateException("ID incompatible");
                String sha=meta.optString("sha256","");
                if(!sha.matches("[a-fA-F0-9]{64}"))throw new IllegalStateException("Hash ausente");
                description="Disponible: v"+meta.optString("version","?")+" · "+
                    meta.optJSONArray("canales").length()+" canales · SHA-256 anunciado";
            }catch(Exception e){
                description="Consulta fallida: "+e.getClass().getSimpleName();
            }finally{if(c!=null)c.disconnect();}
            final String found=description;
            ui.post(()->{
                if(isFinishing()||isDestroyed())return;
                busy=false;
                result.setText(found);
                status.setText("Consulta terminada. Esto no instala ni ejecuta código.");
            });
        });
    }
    @Override protected void onDestroy() {
        worker.shutdownNow();
        ui.removeCallbacksAndMessages(null);
        super.onDestroy();
    }
}
