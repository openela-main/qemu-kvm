/*
 * udev-kvm-check.c
 *
 * Copyright 2018 Red Hat, Inc.
 *
 * This is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 *
 */

#include <ctype.h>
#include <syslog.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DEFAULT 0
#define FACILITY "kvm"
#define SYSCONFIG_KVM "/etc/sysconfig/kvm"

#define COUNT_MSG \
    "%d %s now active"

int get_threshold_from_file(FILE *fp)
{
    static const char key[] = "THRESHOLD=";
    int pos = 0;
    int thres;
    int ch;

start:
    /* State START - at beginning of line, search for beginning of "THRESHOLD="
     * string.
     */
    ch = getc(fp);
    if (ch == EOF) {
        return DEFAULT;
    }
    if (isspace(ch)) {
        goto start;
    }
    if (ch == 'T') {
        pos = 1;
        goto key;
    }
    goto eol;

eol:
    /* State EOL - loop until end of line */
    ch = getc(fp);
    if (ch == EOF) {
        return DEFAULT;
    }
    if (ch == '\n') {
        goto start;
    }
    goto eol;

key:
    /* State KEY - match "THRESHOLD=" string, go to THRESHOLD if found */
    ch = getc(fp);
    if (ch == EOF) {
        return DEFAULT;
    }
    if (ch == key[pos]) {
        pos++;
        if (key[pos] == 0) {
            goto threshold;
        } else {
            goto key;
        }
    }
    goto eol;

threshold:
    /* State THRESHOLD - parse number using fscanf, expect comment or space
     * or EOL.
     */
    ch = getc(fp);
    if (ch == EOF) {
        return DEFAULT;
    }
    if (!isdigit(ch)) {
        goto eol;
    }
    ungetc(ch, fp);
    if (fscanf(fp, "%d", &thres) != 1) {
        return DEFAULT;
    }
    ch = getc(fp);
    if (ch == '#' || ch == EOF || ch == '\n' || isspace(ch)) {
        return thres;
    }
    goto eol;
}

int get_threshold()
{
    FILE *fp = fopen(SYSCONFIG_KVM, "r");
    int val;

    if (!fp) {
        return DEFAULT;
    }

    val = get_threshold_from_file(fp);
    fclose (fp);
    return val;
}

const char *guest(int count)
{
    return (count == 1 ? "guest" : "guests");
}

void emit_count_message(int count)
{
    openlog(FACILITY, LOG_CONS, LOG_USER);
    syslog(LOG_INFO, COUNT_MSG, count, guest(count));
    closelog();
}

int main(int argc, char **argv)
{
    int count, threshold;

    if (argc < 3)
        exit(1);

    count = atoi(argv[1]);
    threshold = get_threshold();

    if (!strcmp(argv[2], "create")) {
        if (threshold == 0 || count > threshold) {
            emit_count_message(count);
        }
    } else {
        if (count >= threshold) {
            emit_count_message(count);
        }
    }

    return 0;
}
