#!/usr/bin/env python3
"""Conservative DaddyLive preview retries; the other sources are untouched."""
from pathlib import Path
import sys

root = Path(sys.argv[1])
p = root / "app/src/main/java/com/infomak/moailite/PreviewPlayback.java"
s = p.read_text(encoding="utf-8")
assert "private int generation;" in s, "Preview generation field changed"
s = s.replace("private int generation;", "private int generation;\n    private int daddyRetries;", 1)
assert "cancel();current=channel;int request=generation;" in s
s = s.replace("cancel();current=channel;int request=generation;",
              "cancel();daddyRetries=0;current=channel;int request=generation;", 1)

needle = "    private void resolve(PluginChannel channel,int request){"
assert needle in s
helper = '''    /** Retry transient DaddyLive resolution/playback failures, not other providers. */
    private boolean retryDaddy(PluginChannel channel, int request, String reason) {
        if (closed || !active || request!=generation || channel==null ||
                channel.getId()==null || !channel.getId().startsWith("moai_daddylive:") ||
                daddyRetries>=3) return false;
        daddyRetries++;
        final int attempt = daddyRetries;
        android.util.Log.w("MOAI-DADDY", "Retry "+attempt+"/3: "+reason);
        release();
        status.setText("DaddyLive: reintentando conexión "+attempt+"/3…");
        handler.postDelayed(() -> {
            if (active && !closed && request==generation && daddyRetries==attempt)
                resolve(channel,request);
        }, attempt*2000L);
        return true;
    }
'''
s=s.replace(needle,helper+needle,1)

needle = '''                        final boolean[] recorded={false};
                        player.addListener'''
replacement = '''                        final boolean[] recorded={false};
                        final int playingAttempt=daddyRetries;
                        if (channel.getId().startsWith("moai_daddylive:")) {
                            handler.postDelayed(() -> {
                                if(active && !closed && request==generation &&
                                   playingAttempt==daddyRetries &&
                                   player!=null && player.getPlaybackState()!=Player.STATE_READY) {
                                    if (!retryDaddy(channel,request,"buffering >45 s"))
                                        status.setText("DaddyLive no respondió tras varios intentos.");
                                }
                            },45000L);
                        }
                        player.addListener'''
assert needle in s
s=s.replace(needle,replacement,1)
old = '''                                if(request==generation)status.setText("Señal no disponible · "+error.getErrorCodeName());'''
new = '''                                if(request!=generation)return;
                                if(!retryDaddy(channel,request,error.getErrorCodeName()))
                                    status.setText("Señal no disponible · "+error.getErrorCodeName());'''
assert old in s
s=s.replace(old,new,1)
old = '''                    }catch(Exception error){release();status.setText("No se pudo abrir la vista previa. Probá otro canal.");}'''
new = '''                    }catch(Exception error){
                        if(!retryDaddy(channel,request,error.getClass().getSimpleName())) {
                            release();status.setText("No se pudo abrir la vista previa. Probá otro canal.");
                        }
                    }'''
assert old in s
s=s.replace(old,new,1)
old = '''                if(active&&!closed&&request==generation){resolving=null;status.setText("No se pudo conectar. Probá otro canal.");}'''
new = '''                if(active&&!closed&&request==generation){
                    resolving=null;
                    if(!retryDaddy(channel,request,error.getClass().getSimpleName()))
                        status.setText("No se pudo conectar. Probá otro canal.");
                }'''
assert old in s
s=s.replace(old,new,1)
p.write_text(s,encoding="utf-8")
print("MOAI DaddyLive: 45-second buffering watchdog, 3 transient retries; other providers unchanged")
