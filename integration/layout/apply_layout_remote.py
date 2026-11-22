#!/usr/bin/env python3
"""MOAI TV layout 42/58 and D-pad only country/category horizontal browsing."""
from pathlib import Path
import sys

root=Path(sys.argv[1])
layout=root/'app/src/main/res/layout/activity_main.xml'
xml=layout.read_text(encoding='utf-8')
old='android:id="@+id/previewPanel" android:layout_width="0dp"\n            android:layout_weight="50"'
new='android:id="@+id/previewPanel" android:layout_width="0dp"\n            android:layout_weight="42"'
assert old in xml
xml=xml.replace(old,new,1)
old='android:id="@+id/channelPanel" android:layout_width="0dp"\n            android:layout_weight="50"'
new='android:id="@+id/channelPanel" android:layout_width="0dp"\n            android:layout_weight="58"'
assert old in xml
xml=xml.replace(old,new,1)
layout.write_text(xml,encoding='utf-8')

java=root/'app/src/main/java/com/infomak/moailite/BrowseStrip.java'
s=java.read_text(encoding='utf-8')
assert 'private void arrow(String label,int direction)' in s
# The 42/58 layout has room for three full country names and four category chips.
assert 'return countries?3:Math.max(2,Math.min(4,width/110));' in s
s=s.replace('return countries?3:Math.max(2,Math.min(4,width/110));',
    'return countries?3:Math.max(2,Math.min(4,width/125));',1)
s=s.replace('    private void focusFirst(){if(getChildCount()>0)getChildAt(0).requestFocus();}',
'''    private void focusFirst(){if(getChildCount()>0)getChildAt(0).requestFocus();}
    private void focusLast(){if(getChildCount()>0)getChildAt(getChildCount()-1).requestFocus();}
    private boolean movePage(int direction){
        int next=page+direction;
        if(next<0 || next*pageSize()>=items.size())return false;
        page=next;
        render();
        post(()->{if(direction>0)focusFirst();else focusLast();});
        return true;
    }
    private android.graphics.drawable.GradientDrawable chip(int fill,int border){
        android.graphics.drawable.GradientDrawable drawable=new android.graphics.drawable.GradientDrawable();
        drawable.setColor(fill);
        drawable.setCornerRadius(dp(19));
        drawable.setStroke(dp(2),border);
        return drawable;
    }
    private android.graphics.drawable.StateListDrawable chipStates(boolean active){
        android.graphics.drawable.StateListDrawable drawable=new android.graphics.drawable.StateListDrawable();
        drawable.addState(new int[]{android.R.attr.state_focused},chip(0xff087f9b,0xff79f5ff));
        drawable.addState(new int[]{android.R.attr.state_pressed},chip(0xff087f9b,0xff79f5ff));
        drawable.addState(new int[]{},chip(active?0xff155c80:0xff173f63,
                                               active?0xff44dbea:0xff284e78));
        return drawable;
    }''',1)
s=s.replace('        if(page>0)arrow("‹",-1);','        // No arrow buttons: move between pages with the TV remote left/right.',1)
s=s.replace('            card.setBackground(Appearance.strip(getContext(),active));',
'''            card.setBackground(chipStates(active));
            card.setOnFocusChangeListener((v,hasFocus)->{
                v.setBackground(chipStates(active));
                v.setScaleX(hasFocus?1.025f:1f);
                v.setScaleY(hasFocus?1.025f:1f);
            });''',1)
old='''            card.setOnKeyListener((v,key,event)->{if(event.getAction()==KeyEvent.ACTION_DOWN&&key==KeyEvent.KEYCODE_DPAD_DOWN){listener.down();return true;}return false;});'''
new='''            final int position=i;
            card.setOnKeyListener((v,key,event)->{
                if(event.getAction()!=KeyEvent.ACTION_DOWN)return false;
                if(key==KeyEvent.KEYCODE_DPAD_DOWN){listener.down();return true;}
                if(key==KeyEvent.KEYCODE_DPAD_RIGHT && position==end-1)
                    return movePage(1);
                if(key==KeyEvent.KEYCODE_DPAD_LEFT && position==start)
                    return movePage(-1);
                return false;
            });'''
assert old in s
s=s.replace(old,new,1)
s=s.replace('        if(end<items.size())arrow("›",1);','        // Page-navigation controls are intentionally hidden.',1)
start=s.index('    private void arrow(String label,int direction)')
end=s.index('    private int dp(int v)',start)
s=s[:start]+s[end:]
java.write_text(s,encoding='utf-8')
print('MOAI GAMER layout: preview 42%, channels 58%; countries/categories D-pad paging; visible focus highlights')
